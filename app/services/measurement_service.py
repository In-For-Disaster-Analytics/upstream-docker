from datetime import datetime
from app.api.v1.schemas.measurement import MeasurementItem, ListMeasurementsResponsePagination
from app.db.repositories.measurement_repository import MeasurementRepository


class MeasurementService:
    def __init__(self, measurement_repository: MeasurementRepository):
        self.measurement_repository = measurement_repository

    def list_measurements(self, sensor_id: int, start_date: datetime, end_date: datetime, min_value: float, max_value: float, page: int = 1, limit: int = 20) -> ListMeasurementsResponsePagination:
        measurements, total_count = self.measurement_repository.list_measurements(sensor_id=sensor_id, start_date=start_date, end_date=end_date, min_value=min_value, max_value=max_value, page=page, limit=limit)
        return ListMeasurementsResponsePagination(
            items=[MeasurementItem(
                id=measurement.measurementid,
                value=measurement.measurementvalue,
                timestamp=measurement.collectiontime,
                collectiontime=measurement.collectiontime,
                description=measurement.description,
                variabletype=measurement.variabletype,
                variablename=measurement.variablename,
                sensorid=measurement.sensorid,
                geometry=measurement.geometry,
            ) for measurement in measurements],
            total=total_count,
            page=page,
            size=limit,
            pages=total_count // limit + 1
        )
