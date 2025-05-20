from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.sensor import SensorItem, GetSensorResponse, ListSensorsResponsePagination, SensorStatistics
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
    variable_name: str | None = Query(None, description="Filter sensors by variable name (partial match)"),
    units: str | None = Query(None, description="Filter sensors by units (exact match)"),
    alias: str | None = Query(None, description="Filter sensors by alias (partial match)"),
    description_contains: str | None = Query(None, description="Filter sensors by text in description (partial match)"),
    postprocess: Optional[bool] = Query(None, description="Filter sensors by postprocess flag"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ListSensorsResponsePagination:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    sensor_repository = SensorRepository(db)
    result, total_count = sensor_repository.get_sensors_by_station_id(
        station_id,
        page,
        limit,
        variable_name=variable_name,
        units=units,
        alias=alias,
        description_contains=description_contains,
        postprocess=postprocess
    )

    return ListSensorsResponsePagination(
        items=[SensorItem(
            id=sensor.sensorid,
            alias=sensor.alias,
            variablename=sensor.variablename,
            description=sensor.description,
            postprocess=sensor.postprocess,
            postprocessscript=sensor.postprocessscript,
            units=sensor.units,
            statistics=SensorStatistics(
                max_value=statistics.max_value,
                min_value=statistics.min_value,
                avg_value=statistics.avg_value,
                stddev_value=statistics.stddev_value,
                percentile_90=statistics.percentile_90,
                percentile_95=statistics.percentile_95,
                percentile_99=statistics.percentile_99,
                count=statistics.count,
                last_measurement_time=statistics.last_measurement_collectiontime,
                last_measurement_value=statistics.last_measurement_value,
                stats_last_updated=statistics.stats_last_updated
            )
        ) for sensor, statistics in result],
        total=total_count,
        page=page,
        size=limit,
        pages=(total_count + limit - 1) // limit,
    )

@router.get("/sensors/{sensor_id}")
async def get_sensor(station_id: int, sensor_id: int, campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GetSensorResponse:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    sensor_repository = SensorRepository(db)
    response = sensor_repository.get_sensor(sensor_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return response
