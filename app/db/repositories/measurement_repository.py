from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

from app.api.v1.schemas.measurement import MeasurementIn
from app.db.models.measurement import Measurement


class MeasurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_measurement(self, request: MeasurementIn, sensor_id: int) -> Measurement:
        # Convert the geometry string to WKTElement for PostGIS
        geometry = WKTElement(request.geometry, srid=4326)

        db_measurement = Measurement(
            sensorid=sensor_id,
            variablename=request.variablename,
            collectiontime=request.collectiontime,
            variabletype=request.variabletype,
            description=request.description,
            measurementvalue=request.measurementvalue,
            geometry=geometry
        )
        self.db.add(db_measurement)
        self.db.commit()
        self.db.refresh(db_measurement)
        return db_measurement

    def get_measurement(self, measurement_id: int) -> Measurement | None:
        return self.db.query(Measurement).get(measurement_id)

    def get_measurements(
        self,
        sensor_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        variable_name: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Measurement], int]:
        query = self.db.query(Measurement)

        if sensor_id:
            query = query.filter(Measurement.sensorid == sensor_id)
        if start_date:
            query = query.filter(Measurement.collectiontime >= start_date)
        if end_date:
            query = query.filter(Measurement.collectiontime <= end_date)
        if min_value is not None:
            query = query.filter(Measurement.measurementvalue >= min_value)
        if max_value is not None:
            query = query.filter(Measurement.measurementvalue <= max_value)
        if variable_name:
            query = query.filter(Measurement.variablename == variable_name)

        # Order by collection time for time series data
        query = query.order_by(Measurement.collectiontime)

        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count

    def delete_measurement(self, measurement_id: int) -> bool:
        db_measurement = self.get_measurement(measurement_id)
        if db_measurement:
            self.db.delete(db_measurement)
            self.db.commit()
            return True
        return False

    def bulk_create_measurements(self, measurements: List[MeasurementIn], sensor_id: int) -> List[Measurement]:
        db_measurements = []
        for measurement in measurements:
            geometry = WKTElement(measurement.geometry, srid=4326)
            db_measurement = Measurement(
                sensorid=sensor_id,
                variablename=measurement.variablename,
                collectiontime=measurement.collectiontime,
                variabletype=measurement.variabletype,
                description=measurement.description,
                measurementvalue=measurement.measurementvalue,
                geometry=geometry
            )
            self.db.add(db_measurement)
            db_measurements.append(db_measurement)

        self.db.commit()
        return db_measurements
