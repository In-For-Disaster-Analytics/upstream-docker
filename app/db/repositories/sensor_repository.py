from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, select, func
from sqlalchemy.sql import text

from app.api.v1.schemas.sensor import SensorIn, GetSensorResponse
from app.db.models.sensor import Sensor
from app.db.models.measurement import Measurement

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
            func.max(Measurement.measurementvalue).label('max_value'),
            func.min(Measurement.measurementvalue).label('min_value')
        ).join(Measurement, Sensor.sensorid == Measurement.sensorid).where(Sensor.sensorid == sensor_id).group_by(Sensor.sensorid)
        result = self.db.execute(stmt).first()

        if result is None:
            return None

        #Get the first and last measurement time
        stmt_first_measurement = select(Measurement).where(Measurement.sensorid == sensor_id).order_by(Measurement.collectiontime.asc()).limit(1)
        first_measurement = self.db.execute(stmt_first_measurement).first()
        if first_measurement is not None:
            first_measurement_time = first_measurement[0].collectiontime
        else:
            first_measurement_time = None

        #Get the last measurement time
        stmt_last_measurement = select(Measurement).where(Measurement.sensorid == sensor_id).order_by(Measurement.collectiontime.desc()).limit(1)
        last_measurement = self.db.execute(stmt_last_measurement).first()
        if last_measurement is not None:
            last_measurement_time = last_measurement[0].collectiontime
        else:
            last_measurement_time = None


        return GetSensorResponse(
            id=result[0].sensorid,
            alias=result[0].alias,
            variablename=result[0].variablename,
            description=result[0].description,
            postprocess=result[0].postprocess,
            postprocessscript=result[0].postprocessscript,
            units=result[0].units,
            max_value=result[1],
            min_value=result[2],
            first_measurement_time=first_measurement_time,
            last_measurement_time=last_measurement_time
        )

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
    ) -> tuple[list[Sensor], int]:
        query = self.db.query(Sensor).filter(Sensor.stationid == station_id)

        # Apply filters if provided
        if variable_name:
            query = query.filter(Sensor.variablename.ilike(f"%{variable_name}%"))
        if units:
            query = query.filter(Sensor.units == units)
        if alias:
            query = query.filter(Sensor.alias.ilike(f"%{alias}%"))
        if description_contains:
            query = query.filter(Sensor.description.ilike(f"%{description_contains}%"))
        if postprocess is not None:
            query = query.filter(Sensor.postprocess == postprocess)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        sensors = query.offset((page - 1) * limit).limit(limit).all()

        return sensors, total_count

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
