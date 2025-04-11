# type: ignore
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
) -> Dict[str, bool | float | str | datetime]:
    t1 = time.time()
    time_file_received = datetime.now()
    print(f'The files are uploaded to the system at {time_file_received}')
    # Initialiaze a response dictionary
    response = {}
    # Initialize an empty dictionary and list to store Sensor and Measurement objects
    #sensors_objs = dict()
    sensor_mapps = [] 
    meas_dicts_all = []
    
    response['uploaded_file_sensors stored in memory'] = upload_file_sensors._in_memory
    response['uploaded_file_measurements stored in memory'] = upload_file_measurements._in_memory
    

    # open the session with database
    with SessionLocal() as session:
        # Create an UploadFileEvent intance and commit
        # to extract id for future reference 
        uploadevent = UploadFileEvent(time=time_file_received)
        session.add(uploadevent)
        session.commit()

        # Open and process the first file - upload_file_sensors
        text_wrapper = TextIOWrapper(upload_file_sensors.file, encoding='utf-8',)
        sensor_data = csv.DictReader(text_wrapper)

        # process each row(dict) from sensor_data
        for sd in sensor_data:
            # validate the row(dict) with Pydantic
            try:
                sensor = SensorCSV.model_validate(sd)
            except ValidationError as exc:
                error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
                raise HTTPException(status_code=400, detail=str(error_messages))

            sensor_dict = sensor.model_dump()
            if sensor_dict['variablename'] is None:
                sensor_dict['variablename'] = 'No BestGuess Formula'

            # add stationid
            sensor_dict['stationid'] = station_id
            # add upload_file_events_id for reference
            sensor_dict['upload_file_events_id'] = uploadevent.id
            # append a dict with attributes of a sensor to sensor_mapps to be commited
            sensor_mapps.append(sensor_dict)
            
        # add all Sensor objects to the session
        session.bulk_insert_mappings(Sensor, sensor_mapps)
        # commit sensors to the database
        session.commit()
        
        # query aliases and sensor ids that have been commited
        alias_to_sensorid = session.query(
            Sensor.alias, Sensor.sensorid
        ).filter(Sensor.upload_file_events_id==uploadevent.id).all()
        
        # reformat the alias_to_sensorid into a {alias: sensorid} map
        alias_to_sensorid_map = {el.alias: el.sensorid for el in alias_to_sensorid}
        
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
            for alias in alias_to_sensorid_map.keys():

                # Validate measurement_value with Pydantic
                try:
                    measurement_value = MeasurementCSV(measurement_value=md[alias])
                except ValidationError as exc:
                    error_messages = [f"Field {err['loc'][0]}: {err['msg']}" for err in exc.errors()]
                    raise HTTPException(status_code=400, detail=str(error_messages))
                
                # create a dict with mesurement's attributes
                measurement_dict = {
                    'stationid': station_id,
                    'collectiontime': collection_time.collection_time,
                    'measurementvalue':measurement_value.measurement_value,
                    'geometry': loc_geometry,
                    'sensorid': alias_to_sensorid_map[alias],
                    'upload_file_events_id': uploadevent.id
                }
                # Store measurement_dicts to commit later
                meas_dicts_all.append(measurement_dict)

        upload_file_measurements.file.close()

        t2 = time.time() # Timestamp when the data processing is complete.
        print('Data processing step is complete.')

        # add and commit the measurements
        session.bulk_insert_mappings(Measurement, meas_dicts_all)
        session.commit()
    
    t3 = time.time()

    response['Data Processing time'] = f"{round(t2-t1, 1)} seconds."
    response['Data Commiting time'] = f"{round(t3-t2, 1)} seconds."

    print(t2-t1)
    print(t3-t2)
    print(response)
    
    return response