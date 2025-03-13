from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.sensor import SensorAndMeasurementIn
from app.api.v1.schemas.user import User
from app.db.models.measurement import Measurement
from app.db.models.sensor import Sensor
from app.db.session import SessionLocal, get_db
from app.db.repositories.sensor_repository import SensorRepository


router = APIRouter(
    prefix="/campaigns/{campaign_id}/stations/{station_id}",
    tags=["campaign_station_sensors"],
)

@router.get("/sensors/{sensor_id}")
async def get_sensor(sensor_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sensor_repository = SensorRepository(db)
    sensor = sensor_repository.get_sensor(sensor_id)
    return sensor

@router.get("/sensor/{sensor_id}")
async def get_sensors(
    campaign_id: int,
    station_id: int,
    sensor_id: int = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_measurement_value: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    limit: int = 1000,
    page: int = 1,
):
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            sensor = session.query(Sensor).get(sensor_id)
            if not sensor:
                raise HTTPException(status_code=404, detail="Sensor not found")

            measurement_query = sensor.measurements.order_by(Measurement.collectiontime)

            if start_date:
                measurement_query = measurement_query.filter(Measurement.collectiontime >= start_date)
            if end_date:
                measurement_query = measurement_query.filter(Measurement.collectiontime <= end_date)
            if min_measurement_value is not None:
                measurement_query = measurement_query.filter(Measurement.measurementvalue > min_measurement_value)

            measurements = measurement_query.limit(limit).offset((page - 1) * limit).all()

            # Convert measurements to dictionaries
            return [
                Measurement(measurementvalue=m.measurementvalue, collectiontime=m.collectiontime)
                for m in measurements
            ]

@router.post("/sensor/", response_model=dict)
async def post_sensor_and_measurement(
    campaign_id: int,
    data: SensorAndMeasurementIn,
    station_id: int,
    current_user: User = Depends(get_current_user),
):
    sensor_data = data.sensor.dict()
    measurement_data_list = [measurement.dict() for measurement in data.measurement]
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            try:
                # Save sensor data
                sensor_data["stationid"] = station_id
                db_sensor = Sensor(**sensor_data)
                session.add(db_sensor)
                session.commit()  # Commit sensor first to get its ID
                session.refresh(db_sensor)

                # Save measurements with the associated sensor
                db_measurements = []
                for measurement_data in measurement_data_list:
                    measurement_data["sensorid"] = db_sensor.sensorid
                    db_measurement = Measurement(**measurement_data)
                    session.add(db_measurement)
                    db_measurements.append(db_measurement)

                session.commit()  # Single commit for all measurements

                # Convert to dictionary representation safely
                measurements_dict = [
                    {
                        key: getattr(measurement, key)
                        for key in measurement.__table__.columns.keys()
                    }
                    for measurement in db_measurements
                ]

                sensor = {
                    key: getattr(db_sensor, key)
                    for key in db_sensor.__table__.columns.keys()
                }

                return {"sensor": sensor, "measurement": measurements_dict}

            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating sensor and measurements: {str(e)}"
                )
