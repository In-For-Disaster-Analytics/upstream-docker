from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.sensor import SensorItem, GetSensorResponse, ListSensorsResponsePagination
from app.api.v1.schemas.user import User
from app.db.session import get_db
from app.db.repositories.sensor_repository import SensorRepository


router = APIRouter(
    prefix="/campaigns/{campaign_id}/stations/{station_id}",
    tags=["sensors"],
)

@router.get("/sensors")
async def list_sensors(
    campaign_id: int,
    station_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ListSensorsResponsePagination:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    sensor_repository = SensorRepository(db)
    sensors = sensor_repository.get_sensors_by_station_id(station_id, page, limit)

    return ListSensorsResponsePagination(
        items=[SensorItem(
            id=sensor.sensorid,
            alias=sensor.alias,
            variablename=sensor.variablename,
            description=sensor.description,
            postprocess=sensor.postprocess,
            postprocessscript=sensor.postprocessscript,
            units=sensor.units,
        ) for sensor in sensors],
        total=len(sensors),
        page=page,
        size=limit,
        pages=len(sensors) // limit + 1,
    )

@router.get("/sensors/{sensor_id}")
async def get_sensor(station_id: int, sensor_id: int, campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GetSensorResponse:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    sensor_repository = SensorRepository(db)
    sensor = sensor_repository.get_sensor(sensor_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return GetSensorResponse(
        id=sensor.sensorid,
        alias=sensor.alias,
        variablename=sensor.variablename,
        description=sensor.description,
        postprocess=sensor.postprocess,
        postprocessscript=sensor.postprocessscript,
        units=sensor.units,
    )

