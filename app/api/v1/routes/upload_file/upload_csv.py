# type: ignore
import time
from datetime import datetime
from typing import Annotated, Dict, Any, List
from pydantic import ValidationError
import pandas as pd

from starlette.formparsers import MultiPartParser
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from pandantic import Pandantic
from app.api.dependencies.auth import get_current_user
from app.api.v1.schemas.user import User
from app.api.v1.schemas.upload_csv_validators import *
from app.db.models.measurement import Measurement
from app.db.models.sensor import Sensor
from app.db.models.upload_file_event import UploadFileEvent
from app.db.session import SessionLocal, get_db
from app.db.repositories.sensor_repository import SensorRepository




# Constants
MultiPartParser.spool_max_size = 500 * 1024 * 1024
BATCH_SIZE = 100000
DEFAULT_VARIABLE_NAME = 'No BestGuess Formula'

router = APIRouter(prefix="/uploadfile_csv", tags=["uploadfile_csv"])

def create_upload_event(session: Session) -> UploadFileEvent:
    """Create and return a new upload file event."""
    upload_event = UploadFileEvent(time=datetime.now())
    session.add(upload_event)
    session.commit()
    return upload_event

def process_batch(batch: List[Dict], session: Session) -> None:
    """Process a batch of measurements and insert to database."""
    if not batch:
        return
    session.bulk_insert_mappings(Measurement, batch)
    session.commit()
    batch.clear()

def validate_sensor_data(sensor_data: Dict) -> SensorCSV:
    """Validate sensor data using Pydantic model."""
    try:
        return SensorCSV.model_validate(sensor_data)
    except ValidationError as exc:
        error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
        raise HTTPException(status_code=400, detail=str(error_messages))

def validate_measurement_data(measurement_data: Dict) -> tuple[CollTimeCSV, LocationCSV]:
    """Validate measurement data using Pydantic models."""
    try:
        collection_time = CollTimeCSV(collection_time=measurement_data['collectiontime'])
        location = LocationCSV(long_deg=measurement_data['Lon_deg'], lat_deg=measurement_data['Lat_deg'])
        return collection_time, location
    except ValidationError as exc:
        error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
        raise HTTPException(status_code=400, detail=str(error_messages))

def process_sensors_file(file: UploadFile, station_id: int, upload_event_id: int, session: Session) -> Dict[str, int]:
    """Process the sensors CSV file and return a mapping of aliases to sensor IDs."""
    # Read CSV using pandas
    df_sensors = pd.read_csv(file.file, keep_default_na=False, na_values=[])
    sensor_maps = []
    validator = Pandantic(schema=SensorCSV)
    # Validate with error raising
    try:
        validator.validate(dataframe=df_sensors, errors="raise")
    except ValueError:
        print("Validation failed!")

    # Process each row
    for _, sensor_row in df_sensors.iterrows():
        sensor = validate_sensor_data(sensor_row.to_dict())
        sensor_dict = sensor.model_dump()
        sensor_dict['variablename'] = sensor_dict['variablename'] or DEFAULT_VARIABLE_NAME
        sensor_dict['stationid'] = station_id
        sensor_dict['upload_file_events_id'] = upload_event_id
        sensor_maps.append(sensor_dict)

    session.bulk_insert_mappings(Sensor, sensor_maps)
    session.commit()

    # Get sensor mapping
    alias_to_sensorid = session.query(
        Sensor.alias, Sensor.sensorid
    ).filter(Sensor.upload_file_events_id == upload_event_id).all()

    return {el.alias: el.sensorid for el in alias_to_sensorid}

def create_measurement_dict(
    station_id: int,
    collection_time: datetime,
    measurement_value: float,
    geometry: WKTElement,
    sensor_id: int,
    upload_event_id: int
) -> Dict:
    """Create a measurement dictionary with all required fields."""
    return {
        'stationid': station_id,
        'collectiontime': collection_time,
        'measurementvalue': measurement_value,
        'geometry': geometry,
        'sensorid': sensor_id,
        'upload_file_events_id': upload_event_id
    }

def process_measurements_file(
    file: UploadFile,
    station_id: int,
    alias_to_sensorid_map: Dict[str, int],
    upload_event_id: int,
    session: Session
) -> int:
    """Process the measurements CSV file and return total number of measurements processed."""
    # Read CSV using pandas
    df_measurements = pd.read_csv(
        file.file,
        keep_default_na=False,  # Prevent NaN creation
        na_values=[''],         # Only empty strings become NaN
        dtype={'Lon_deg': 'float64', 'Lat_deg': 'float64'},  # Pre-specify dtypes
        parse_dates=['collectiontime'],  # Parse dates during read
        date_parser=pd.to_datetime,  # Use fast date parser
        sort_values=['collectiontime']
    )
    measurement_batch = []
    total_measurements = 0


    sensor_aliases = list(alias_to_sensorid_map.keys())

    # Convert all sensor columns at once (vectorized operation)
    for alias in sensor_aliases:
        if alias in df_measurements.columns:
            df_measurements[alias] = pd.to_numeric(df_measurements[alias], errors='coerce')

    # 3. OPTIMIZATION: Pre-compute geometry for all rows (vectorized)
    # This is MUCH faster than creating WKTElement in the loop
    df_measurements['geometry_str'] = 'Point (' + df_measurements['Lon_deg'].astype(str) + ' ' + df_measurements['Lat_deg'].astype(str) + ')'


    for alias, sensor_id in alias_to_sensorid_map.items():
        if alias not in df_measurements.columns:
            continue
        sensor_measurements = [
            {
                'stationid': station_id,
                'collectiontime': row['collectiontime'],
                'measurementvalue': row[alias],
                'geometry': WKTElement(row['geometry_str'], srid=4326),
                'sensorid': sensor_id,
                'upload_file_events_id': upload_event_id
            }
            for _, row in df_measurements.iterrows()
            if pd.notna(row[alias])  # Skip NaN values
        ]
        measurement_batch.extend(sensor_measurements)
        total_measurements += 1
        if len(measurement_batch) >= BATCH_SIZE:
            process_batch(measurement_batch, session)

    if measurement_batch:
        process_batch(measurement_batch, session)

    return total_measurements

def update_sensor_statistics(sensor_repository: SensorRepository, alias_to_sensorid_map: Dict[str, int]) -> None:
    """Update statistics for all sensors."""
    for sensor_id in alias_to_sensorid_map.values():
        sensor_repository.delete_sensor_statistics(sensor_id)
        sensor_repository.refresh_sensor_statistics(sensor_id)

@router.post("/campaign/{campaign_id}/station/{station_id}/sensor")
def post_sensor_and_measurement(
    campaign_id: int,
    station_id: int,
    upload_file_sensors: Annotated[UploadFile, File(description="File with sensors.")],
    upload_file_measurements: Annotated[UploadFile, File(description="File with measurements.")],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Process sensor and measurement files and store data in the database."""
    start_time = time.time()
    time_file_received = datetime.now()

    response = {
        'uploaded_file_sensors stored in memory': upload_file_sensors._in_memory,
        'uploaded_file_measurements stored in memory': upload_file_measurements._in_memory
    }

    try:
        with SessionLocal() as session:
            # Create upload event
            upload_event = create_upload_event(session)

            # Process sensors file
            alias_to_sensorid_map = process_sensors_file(
                upload_file_sensors, station_id, upload_event.id, session
            )
            upload_file_sensors.file.close()

            # Process measurements file
            total_measurements = process_measurements_file(
                upload_file_measurements, station_id, alias_to_sensorid_map, upload_event.id, session
            )
            upload_file_measurements.file.close()

        # Update sensor statistics
        # sensor_repository = SensorRepository(db)
        # update_sensor_statistics(sensor_repository, alias_to_sensorid_map)

        processing_time = time.time() - start_time
        response.update({
            'Total measurements processed': total_measurements,
            'Data Processing time': f"{round(processing_time, 1)} seconds."
        })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
