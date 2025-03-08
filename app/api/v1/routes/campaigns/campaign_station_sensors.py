from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.db.models.sensor import Sensor
from app.db.models.measurement import Measurement
from app.db.models.location import Locations
from app.basemodels import SensorAndMeasurementIn, User
from app.db.session import SessionLocal

router = APIRouter(prefix="/campaigns/{campaign_id}/stations/{station_id}", tags=["campaign_station_sensors"])

# Route to retrieve sensor data based on specified parameters (e.g., sensor_id, date range, minimum measurement value)
@router.get("/sensor/{sensor_id}")
async def get_sensors(
    campaign_id:int,
    station_id: int,
    sensor_id: int=None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_measurement_value: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            db_sensor = session.query(Sensor).filter(Sensor.sensorid == sensor_id).join(Sensor.measurement)

            if start_date:
                db_sensor = db_sensor.filter(Sensor.measurement.any(Measurement.collectiontime >= start_date))
            if end_date:
                db_sensor = db_sensor.filter(Sensor.measurement.any(Measurement.collectiontime <= end_date))
            if min_measurement_value is not None:
                db_sensor = db_sensor.filter(Measurement.measurementvalue > min_measurement_value)
            return  db_sensor.all()


# Route to create a new sensor and associated measurements for a specific station and campaign
@router.post("/sensor/", response_model=dict)
async def post_sensor_and_measurement(campaign_id:int , data: SensorAndMeasurementIn, station_id: int, current_user: User = Depends(get_current_user)):
    sensor_data = data.sensor.dict()
    measurement_data_list = [measurement.dict() for measurement in data.measurement]
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
            # Save measurements with the associated sensor
            db_measurements = []
            location_data = {}
            for measurement_data in measurement_data_list:
                measurement_data['sensorid'] = db_sensor.sensorid
                location_data['geometry'] = measurement_data.pop('geometry', None)
                location_data['geometry'] = WKTElement(location_data['geometry'], srid=4326)
                location_data['stationid'] = station_id
                location_data['collectiontime']=measurement_data['collectiontime']
                db_measurement = Measurement(**measurement_data)
                session.add(db_measurement)
                try:
                    # Try to find an existing location
                    db_location = session.query(Locations).filter_by(
                        stationid=location_data['stationid'],
                        collectiontime=location_data['collectiontime'],
                        geometry=location_data['geometry'],
                    ).one()

                except NoResultFound:
                    # If no existing location is found, create a new one
                    db_location = Locations(**location_data)
                    session.add(db_location)

                session.commit()
                session.refresh(db_measurement)
                db_measurements.append(db_measurement.__dict__)


            sensor = {key: getattr(db_sensor, key) for key in db_sensor.__table__.columns.keys()}

            return {"sensor":sensor, "measurement": db_measurements}

