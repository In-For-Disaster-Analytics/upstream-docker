from typing import Annotated
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from geoalchemy2 import WKTElement
from app.basemodels import SensorAndMeasurementIn, User
from app.db.models.sensor import Sensor
from app.db.models.measurement import Measurement
from app.db.models.location import Locations
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission

from sqlalchemy.orm.exc import NoResultFound
from app.db.session import SessionLocal

router = APIRouter(prefix="/uploadfile", tags=["uploadfile"])
@router.post("/campaign/{campaign_id}/station/{station_id}/sensor/")
def post_sensor_and_measurement(
    campaign_id:int,
    uploaded_file: Annotated[UploadFile, File(...)],
    station_id: int,
    current_user: User = Depends(get_current_user)
):

    # file_bytes = uploaded_file.file.read()
    # buffer = StringIO(file_bytes.decode('utf-8'))
    # json_data = json.load(buffer)
    # buffer.close()
    # uploaded_file.file.close()

    # data = SensorAndMeasurementIn(**json_data)

    # print(data.dict())


    data = json.load(uploaded_file.file)
    uploaded_file.file.close()

    data = SensorAndMeasurementIn(**data)
    sensor_data = data.sensor.dict()
    measurement_data_list = [measurement.dict() for measurement in data.measurement]
    del data

    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:

            # Save sensor data
            sensor_data['stationid']=station_id

            db_sensor = Sensor(**sensor_data)
            session.add(db_sensor)
            session.commit()
            session.refresh(db_sensor)
            db_sensor = session.query(Sensor).filter(Sensor.sensorid == db_sensor.sensorid).first()
            if not db_sensor:
                raise HTTPException(status_code=500, detail="Failed to retrieve sensor data")

            # Retrieve and save location data
            location_data = []
            counter = 0
            for measurement_data in measurement_data_list:

                loc_geometry = measurement_data.pop('geometry', None)
                loc_geometry = WKTElement(loc_geometry, srid=4326)
                loc_collectiontime = measurement_data['collectiontime']
                location_instance = Locations(
                    stationid = station_id,
                    collectiontime = loc_collectiontime,
                    geometry = loc_geometry
                )

                location_data.append(location_instance)

                try:
                    # Try to find an existing location
                    db_location = session.query(Locations).filter_by(
                        collectiontime=loc_collectiontime,
                        geometry=loc_geometry,
                    ).one()

                except NoResultFound:
                    # If no existing location is found, create a new one
                    session.add(location_instance)

                counter += 1
                if counter % 1000 == 0:
                    print(f'Locations processed: {counter}')

            session.commit()

            # Save measurements with the associated sensor
            counter = 0
            for i, measurement_data in enumerate(measurement_data_list):
                measurement_data['sensorid'] = db_sensor.sensorid
                measurement_data['locationid'] = location_data[i].locationid
                db_measurement = Measurement(**measurement_data)
                session.add(db_measurement)

                counter += 1
                if counter % 1000 == 0:
                    print(f'Measurements processed: {counter}')

            session.commit()

    return {'Result': 'The data was uploaded.'}