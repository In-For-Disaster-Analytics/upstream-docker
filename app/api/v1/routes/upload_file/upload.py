import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from geoalchemy2 import WKTElement
from sqlalchemy.orm.exc import NoResultFound

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.sensor import SensorAndMeasurementIn
from app.api.v1.schemas.user import User
from app.db.models.measurement import Measurement
from app.db.models.sensor import Sensor
from app.db.session import SessionLocal

router = APIRouter(prefix="/uploadfile", tags=["uploadfile"])


@router.post("/campaign/{campaign_id}/station/{station_id}/sensor/")
def post_sensor_and_measurement(
    campaign_id: int,
    uploaded_file: Annotated[UploadFile, File(...)],
    station_id: int,
    current_user: User = Depends(get_current_user),
):

    data = json.load(uploaded_file.file)
    uploaded_file.file.close()

    data = SensorAndMeasurementIn(**data)
    sensor_data = data.sensor.dict()
    measurement_data_list = [measurement.dict() for measurement in data.measurement]
    del data

    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            # Save sensor data
            sensor_data["stationid"] = station_id
            db_sensor = Sensor(**sensor_data)
            session.add(db_sensor)
            session.commit()
            session.refresh(db_sensor)

            db_sensor = (
                session.query(Sensor)
                .filter(Sensor.sensorid == db_sensor.sensorid)
                .first()
            )
            if not db_sensor:
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve sensor data"
                )

            # Save measurements with the associated sensor
            counter = 0
            for i, measurement_data in enumerate(measurement_data_list):
                measurement_data["sensorid"] = db_sensor.sensorid
                db_measurement = Measurement(**measurement_data)
                session.add(db_measurement)

                counter += 1
                if counter % 1000 == 0:
                    print(f"Measurements processed: {counter}")

            session.commit()

    return {"Result": "The data was uploaded."}
