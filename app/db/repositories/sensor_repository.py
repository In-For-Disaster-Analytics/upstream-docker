from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import Row, Sequence, or_, select, func
from sqlalchemy.sql import text

from app.api.v1.schemas.sensor import SensorIn, GetSensorResponse, SensorStatistics as SensorStatisticsSchema
from app.db.models.sensor import Sensor
from app.db.models.measurement import Measurement
from app.db.models.sensor_statistics import SensorStatistics

class SensorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_sensor(self, request: SensorIn, station_id: int) -> Sensor:
        db_sensor = Sensor(
            stationid=station_id,
            alias=request.alias,
            description=request.description,
            postprocess=request.postprocess,
            postprocessscript=request.postprocessscript,
            units=request.units,
            variablename=request.variablename
        )
        self.db.add(db_sensor)
        self.db.commit()
        self.db.refresh(db_sensor)
        return db_sensor

    def get_sensor(self, sensor_id: int) -> GetSensorResponse | None:
        stmt = select(
            Sensor,
            SensorStatistics
        ).outerjoin(
            SensorStatistics,
            Sensor.sensorid == SensorStatistics.sensorid
        ).where(Sensor.sensorid == sensor_id)

        result = self.db.execute(stmt).first()

        if result is None:
            return None

        sensor, statistics = result

        return GetSensorResponse(
            id=sensor.sensorid,
            alias=sensor.alias,
            variablename=sensor.variablename,
            description=sensor.description,
            postprocess=sensor.postprocess,
            postprocessscript=sensor.postprocessscript,
            units=sensor.units,
            statistics=SensorStatisticsSchema(
                max_value=statistics.max_value if statistics else None,
                min_value=statistics.min_value if statistics else None,
                avg_value=statistics.avg_value if statistics else None,
                stddev_value=statistics.stddev_value if statistics else None,
                percentile_90=statistics.percentile_90 if statistics else None,
                percentile_95=statistics.percentile_95 if statistics else None,
                percentile_99=statistics.percentile_99 if statistics else None,
                count=statistics.count if statistics else None,
                first_measurement_value=statistics.first_measurement_value if statistics else None,
                first_measurement_collectiontime=statistics.first_measurement_collectiontime if statistics else None,
                last_measurement_time=statistics.last_measurement_collectiontime if statistics else None,
                last_measurement_value=statistics.last_measurement_value if statistics else None,
                stats_last_updated=statistics.stats_last_updated if statistics else None
            )
        )

    def delete_sensor_statistics(self, sensor_id: int) -> bool:
        self.db.query(SensorStatistics).filter(SensorStatistics.sensorid == sensor_id).delete()
        self.db.commit()
        return True

    def refresh_sensor_statistics(self, sensor_id: int) -> bool:
        self.db.execute(text("SELECT refresh_outdated_sensor_statistics(:sensor_id);"), {"sensor_id": sensor_id})
        self.db.commit()
        return True

    def get_sensors_by_station_id(
        self,
        station_id: int,
        page: int = 1,
        limit: int = 20,
        variable_name: str | None = None,
        units: str | None = None,
        alias: str | None = None,
        description_contains: str | None = None,
        postprocess: bool | None = None,
    ) -> Tuple[list[Row[Tuple[Sensor, SensorStatistics]]], int]:
        count_stmt = select(func.count()).select_from(Sensor).where(Sensor.stationid == station_id)
        stmt = select(Sensor, SensorStatistics).outerjoin(SensorStatistics, Sensor.sensorid == SensorStatistics.sensorid)
        stmt = stmt.where(Sensor.stationid == station_id).limit(limit).offset((page - 1) * limit)
        if variable_name:
            stmt = stmt.where(Sensor.variablename.ilike(f"%{variable_name}%"))
            count_stmt = count_stmt.where(Sensor.variablename.ilike(f"%{variable_name}%"))
        if units:
            stmt = stmt.where(Sensor.units == units)
            count_stmt = count_stmt.where(Sensor.units == units)
        if alias:
            stmt = stmt.where(Sensor.alias.ilike(f"%{alias}%"))
            count_stmt = count_stmt.where(Sensor.alias.ilike(f"%{alias}%"))
        if description_contains:
            stmt = stmt.where(Sensor.description.ilike(f"%{description_contains}%"))
            count_stmt = count_stmt.where(Sensor.description.ilike(f"%{description_contains}%"))
        if postprocess is not None:
            stmt = stmt.where(Sensor.postprocess == postprocess)
            count_stmt = count_stmt.where(Sensor.postprocess == postprocess)
        result = list(self.db.execute(stmt).all())
        total_count = self.db.execute(count_stmt).scalar_one()
        return result, total_count

    def get_sensors(
        self,
        station_id: Optional[int] = None,
        variable_name: Optional[str] = None,
        postprocess: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Sensor], int]:
        query = self.db.query(Sensor)
        if station_id:
            query = query.filter(Sensor.stationid == station_id)
        if variable_name:
            query = query.filter(Sensor.variablename == variable_name)
        if postprocess is not None:
            query = query.filter(Sensor.postprocess == postprocess)

        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count

    def delete_sensor(self, sensor_id: int) -> bool:
        db_sensor = self.get_sensor(sensor_id)
        if db_sensor:
            self.db.delete(db_sensor)
            self.db.commit()
            return True
        return False

    def list_sensor_variables(self) -> list[str]:
        return [row[0] for row in self.db.query(Sensor.variablename).distinct().all()]
