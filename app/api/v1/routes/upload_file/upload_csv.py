import csv 
import time
from datetime import datetime
from io import TextIOWrapper
from typing import Annotated, Dict, Any
from pydantic import ValidationError

from starlette.formparsers import MultiPartParser

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from geoalchemy2 import WKTElement
from sqlalchemy.orm.exc import NoResultFound

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.user import User
from app.api.v1.schemas.upload_csv_validators import *
from app.db.models.measurement import Measurement
from app.db.models.sensor import Sensor
from app.db.models.upload_file_event import UploadFileEvent
from app.db.session import SessionLocal

router = APIRouter(prefix="/uploadfile_csv", tags=["uploadfile_csv"])

MultiPartParser.spool_max_size = 500 * 1024 * 1024

@router.post("/campaign/{campaign_id}/station/{station_id}/sensor")
def post_sensor_and_measurement(
    campaign_id: int,
    station_id: int,
    upload_file_sensors: Annotated[UploadFile, File(description="File with sensors.")],
    upload_file_measurements: Annotated[UploadFile, File(description="File with measurements.")],
    current_user: User = Depends(get_current_user),
) -> Dict[str, bool | float | str ]:
    t1 = time.time()
    time_file_received = datetime.now()
    print(f'The files are uploaded to the system at {time_file_received}')
    uploadevent = UploadFileEvent(time=time_file_received)

    # Initialiaze a response dictionary
    response = {}

    # Initialize an empty dictionary and list to store Sensor and Measurement objects
    sensors_objs = dict()
    meas_objs_all = []

    response['uploaded_file_sensors stored in memory'] = upload_file_sensors._in_memory
    response['uploaded_file_measurements stored in memory'] = upload_file_measurements._in_memory

    # Open and process the first file - upload_file_sensors
    text_wrapper = TextIOWrapper(upload_file_sensors.file, encoding='utf-8',)
    sensor_data = csv.DictReader(text_wrapper)

    for sd in sensor_data:
        
        try:
            sensor = SensorCSV.model_validate(sd)
        except ValidationError as exc:
            error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
            raise HTTPException(status_code=400, detail=str(error_messages))
        
        sensor_dict = sensor.model_dump()
        if sensor_dict['variablename'] is None:
            sensor_dict['variablename'] = 'No BestGuess Formula'
        
        sensor_dict['upload_file_event'] = uploadevent
        sensors_objs[sensor.alias] = Sensor(**sensor_dict)

    upload_file_sensors.file.close()
    
    # Open and process the second file - upload_file_measurements
    text_wrapper = TextIOWrapper(upload_file_measurements.file, encoding='utf-8-sig', errors='replace')
    measurement_data = csv.DictReader(text_wrapper)

    # iterate over each dictionary(i.e., row) in measurement data
    counter = 0
    for md in measurement_data:
        
        counter += 1
        if counter % 100 == 0:
            print(counter)
        
        # Validate collection_time and location with Pydantic
        try:
            collection_time = CollTimeCSV(collection_time=md['collectiontime']) # md['Time_CDT'])
            location = LocationCSV(long_deg=md['Lon_deg'], lat_deg=md['Lat_deg'])
        except ValidationError as exc:
            error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
            raise HTTPException(status_code=400, detail=str(error_messages))
        
        # Process location data and create an instance of Locations
        loc_geometry = f"Point ({location.long_deg} {location.lat_deg})"
        loc_geometry = WKTElement(loc_geometry, srid=4326)
        # iterate over each alias in sensors_objs
        for al in sensors_objs.keys():
            
            # Validate measurement_value with Pydantic
            try:
                measurement_value = MeasurementCSV(measurement_value=md[al])
            except ValidationError as exc:
                error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
                raise HTTPException(status_code=400, detail=str(error_messages))
        

            # Create an instance of Measurement
            measurement = Measurement(
                stationid=station_id,
                collectiontime=collection_time.collection_time,
                measurementvalue=measurement_value.measurement_value,
                geometry=loc_geometry,
                sensor=sensors_objs[al],
                upload_file_event=uploadevent
            )

            meas_objs_all.append(measurement)
    
    upload_file_measurements.file.close()

    t2 = time.time() # Timestamp when the data processing is complete.
    print('Data processing step is complete.')

    with SessionLocal() as session:    
        session.add_all(meas_objs_all)
        session.commit()
    
    t3 = time.time()

    response['Data Processing time'] = f"{round(t2-t1, 1)} seconds."
    response['Data Commiting time'] = f"{round(t3-t2, 1)} seconds."

    print(t2-t1)
    print(t3-t2)
    print(response)

    return response