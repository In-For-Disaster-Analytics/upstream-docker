from datetime import datetime
import pandas as pd
from starlette.formparsers import MultiPartParser
from fastapi import HTTPException, UploadFile
from pandantic import Pandantic
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
from app.db.models.measurement import Measurement
from app.db.repositories.sensor_repository import SensorRepository
from app.db.repositories.measurement_repository import MeasurementRepository
from app.db.models.sensor import Sensor
from app.api.v1.schemas.sensor import SensorIn

# Constants
MultiPartParser.spool_max_size = 500 * 1024 * 1024
BATCH_SIZE = 10000
DEFAULT_VARIABLE_NAME = 'No BestGuess Formula'


def process_batch(batch: list[dict[str, int | datetime | float | WKTElement]], session: Session) -> None:
    """Process a batch of measurements and insert to database."""
    if not batch:
        return
    session.bulk_insert_mappings(Measurement, batch) # type: ignore[arg-type]
    session.commit()
    batch.clear()

def process_sensors_file(file: UploadFile, station_id: int, upload_event_id: int, session: Session) -> dict[str, int]:
    """Process the sensors CSV file and return a mapping of aliases to sensor IDs."""
    # Read CSV using pandas
    sensor_repository = SensorRepository(session)
    df_sensors = pd.read_csv(file.file, keep_default_na=False, na_values=[])
    sensor_maps : list[Sensor]= []
    existing_sensors : list[Sensor]= []
    validator = Pandantic(schema=SensorIn)

    try:
        validator.validate(dataframe=df_sensors, errors="raise")
    except ValueError:
        print(f"Validation failed! {validator.errors}")
        raise HTTPException(status_code=400, detail="Validation failed!")

    # Process each row
    for _, sensor_row in df_sensors.iterrows():
        sensor: Sensor = Sensor(
            alias=sensor_row.alias,
            variablename=sensor_row.variablename if 'variablename' in sensor_row else DEFAULT_VARIABLE_NAME,
            stationid=station_id,
            upload_file_events_id=upload_event_id,
            units=sensor_row.units if 'units' in sensor_row else None,
            postprocess=sensor_row.postprocess if 'postprocess' in sensor_row else None,
            postprocessscript=sensor_row.postprocessscript if 'postprocessscript' in sensor_row else None,
        )
        existing_sensor = sensor_repository.get_sensor_by_alias_and_station_id(str(sensor.alias), station_id)
        if existing_sensor is None:
            sensor_maps.append(sensor)
        else:
            print(f"Sensor {sensor.alias}  already exists in the database ")
            existing_sensors.append(existing_sensor)
    sensor_repository.create_sensors(sensor_maps)

    # Get sensor mapping
    alias_to_sensorid = session.query(
        Sensor.alias, Sensor.sensorid
    ).filter(Sensor.upload_file_events_id == upload_event_id).all()

    response: dict[str, int] = {}
    for el in alias_to_sensorid:
        if el.alias is not None:
          response[el.alias] = el.sensorid
    for sensor in existing_sensors:
        if sensor.alias is not None:
          response[sensor.alias] = sensor.sensorid

    return response

def create_measurement_dict(
    station_id: int,
    collection_time: datetime,
    measurement_value: float,
    geometry: WKTElement,
    sensor_id: int,
    upload_event_id: int
) -> dict[str, int | datetime | float | WKTElement]:
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
    alias_to_sensorid_map: dict[str, int],
    upload_event_id: int,
    session: Session
) -> int:
    """Process the measurements CSV file and return total number of measurements processed."""
    measurement_repository = MeasurementRepository(session)

    # Read CSV using pandas
    df = pd.read_csv(
        file.file,
        keep_default_na=False,  # Prevent NaN creation
        na_values=[''],         # Only empty strings become NaN
        dtype={'Lon_deg': 'str', 'Lat_deg': 'str'},  # Pre-specify dtypes
        parse_dates=['collectiontime'],  # Parse dates during read
        date_parser=pd.to_datetime,  # Use fast date parser
    ) # type: ignore[call-overload]
    df = df.sort_values(by='collectiontime')

    measurement_batch = []
    total_measurements = 0

    sensor_aliases = list(alias_to_sensorid_map.keys())

    # Convert all sensor columns at once (vectorized operation)
    for alias in sensor_aliases:
        if alias in df.columns:
            df[alias] = pd.to_numeric(df[alias], errors='coerce')

    # 3. OPTIMIZATION: Pre-compute geometry for all rows (vectorized)
    df['geometry_str'] = 'Point (' + df['Lon_deg'] + ' ' + df['Lat_deg'] + ')'

    for alias, sensor_id in alias_to_sensorid_map.items():
        if alias not in df.columns:
            continue
        latest_measurement = measurement_repository.get_latest_measurement_by_sensor_id(sensor_id)
        df_filtered = df[df['collectiontime'] > latest_measurement.collectiontime] if latest_measurement else df

        # Create measurements using vectorized operations
        valid_mask = pd.notna(df_filtered[alias])
        if not valid_mask.any():
            continue

        sensor_measurements = [
            {
                'stationid': station_id,
                'collectiontime': time,
                'measurementvalue': value,
                'geometry': WKTElement(geom, srid=4326),
                'sensorid': sensor_id,
                'variablename': alias,
                'upload_file_events_id': upload_event_id
            }
            for time, value, geom in zip(
                df_filtered.loc[valid_mask, 'collectiontime'],
                df_filtered.loc[valid_mask, alias],
                df_filtered.loc[valid_mask, 'geometry_str']
            )
        ]
        measurement_batch.extend(sensor_measurements)
        if len(measurement_batch) >= BATCH_SIZE:
            process_batch(measurement_batch, session)
            total_measurements += len(measurement_batch)
            measurement_batch = []

    if measurement_batch:
        process_batch(measurement_batch, session)
        total_measurements += len(measurement_batch)
        measurement_batch = []

    return total_measurements

def update_sensor_statistics(sensor_repository: SensorRepository, alias_to_sensorid_map: dict[str, int]) -> None:
    """Update statistics for all sensors."""
    for sensor_id in alias_to_sensorid_map.values():
        sensor_repository.delete_sensor_statistics(sensor_id)
        sensor_repository.refresh_sensor_statistics(sensor_id)