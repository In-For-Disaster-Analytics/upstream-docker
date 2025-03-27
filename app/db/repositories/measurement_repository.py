from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from sqlalchemy import func
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

    def list_measurements(
        self,
        sensor_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        variable_name: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Measurement, str], int]:
        query = self.db.query(Measurement, func.ST_AsGeoJSON(Measurement.geometry).label("geometry"))

        if sensor_id:
            query = query.filter(Measurement.sensorid == sensor_id)
        if start_date is not None:
            if isinstance(start_date, int):
                start_date = datetime.fromtimestamp(start_date)
            query = query.filter(Measurement.collectiontime >= start_date)
        if end_date is not None:
            if isinstance(end_date, int):
                end_date = datetime.fromtimestamp(end_date)
            query = query.filter(Measurement.collectiontime <= end_date)
        if min_value is not None:
            query = query.filter(Measurement.measurementvalue >= min_value)
        if max_value is not None:
            query = query.filter(Measurement.measurementvalue <= max_value)
        if variable_name:
            query = query.filter(Measurement.variablename == variable_name)

        # Order by collection time for time series data
        query = query.order_by(Measurement.collectiontime.desc())

        total_count = query.count()

        results_paginated = query.offset((page - 1) * limit).limit(limit).all()

        # Create a separate query for stats without ordering
        stats_query = self.db.query(Measurement)
        if sensor_id:
            stats_query = stats_query.filter(Measurement.sensorid == sensor_id)
        if start_date is not None:
            if isinstance(start_date, int):
                start_date = datetime.fromtimestamp(start_date)
            stats_query = stats_query.filter(Measurement.collectiontime >= start_date)
        if end_date is not None:
            if isinstance(end_date, int):
                end_date = datetime.fromtimestamp(end_date)
            stats_query = stats_query.filter(Measurement.collectiontime <= end_date)
        if min_value is not None:
            stats_query = stats_query.filter(Measurement.measurementvalue >= min_value)
        if max_value is not None:
            stats_query = stats_query.filter(Measurement.measurementvalue <= max_value)
        if variable_name:
            stats_query = stats_query.filter(Measurement.variablename == variable_name)

        stats_min_value = stats_query.with_entities(func.min(Measurement.measurementvalue)).scalar()
        stats_max_value = stats_query.with_entities(func.max(Measurement.measurementvalue)).scalar()
        stats_average_value = stats_query.with_entities(func.avg(Measurement.measurementvalue)).scalar()

        return results_paginated, total_count, stats_min_value, stats_max_value, stats_average_value

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
