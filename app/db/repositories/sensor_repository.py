from typing import Optional, List

from sqlalchemy.orm import Session

from app.api.v1.schemas.sensor import SensorIn
from app.db.models.sensor import Sensor


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

    def get_sensor(self, sensor_id: int) -> Sensor | None:
        return self.db.query(Sensor).get(sensor_id)

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
