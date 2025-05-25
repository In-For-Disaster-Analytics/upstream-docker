from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.sensor import SensorItem, GetSensorResponse, ListSensorsResponsePagination, SensorStatistics
from app.api.v1.schemas.user import User
from app.db.session import get_db
from app.db.repositories.sensor_repository import SensorRepository, SortField


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
    sort_by: Optional[SortField] = Query(None, description="Sort sensors by field"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
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
        postprocess=postprocess,
        sort_by=sort_by,
        sort_order=sort_order
    )

    response = []

    for sensor, statistics in result:
        if statistics is None:
            statistics = SensorStatistics()
        else:
            statistics = SensorStatistics(
                max_value=statistics.max_value if statistics.max_value is not None else None,
                min_value=statistics.min_value if statistics.min_value is not None else None,
                avg_value=statistics.avg_value if statistics.avg_value is not None else None,
                stddev_value=statistics.stddev_value if statistics.stddev_value is not None else None,
                percentile_90=statistics.percentile_90 if statistics.percentile_90 is not None else None,
                percentile_95=statistics.percentile_95 if statistics.percentile_95 is not None else None,
                percentile_99=statistics.percentile_99 if statistics.percentile_99 is not None else None,
                count=statistics.count if statistics.count is not None else None,
                last_measurement_time=statistics.last_measurement_collectiontime if statistics.last_measurement_collectiontime is not None else None,
                last_measurement_value=statistics.last_measurement_value if statistics.last_measurement_value is not None else None,
                first_measurement_value=statistics.first_measurement_value if statistics.first_measurement_value is not None else None,
                first_measurement_collectiontime=statistics.first_measurement_collectiontime if statistics.first_measurement_collectiontime is not None else None,
                stats_last_updated=statistics.stats_last_updated if statistics.stats_last_updated is not None else None
            )

        response.append(SensorItem(
            id=sensor.sensorid,
            alias=sensor.alias,
            variablename=sensor.variablename,
            description=sensor.description,
            postprocess=sensor.postprocess,
            postprocessscript=sensor.postprocessscript,
            units=sensor.units,
            statistics=statistics
        ))

    return ListSensorsResponsePagination(
        items=response,
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
