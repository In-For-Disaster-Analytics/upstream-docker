from datetime import datetime
import json
from app.api.v1.schemas.measurement import MeasurementItem, ListMeasurementsResponsePagination
from app.db.repositories.measurement_repository import MeasurementRepository


class MeasurementService:
    def __init__(self, measurement_repository: MeasurementRepository):
        self.measurement_repository = measurement_repository

    def list_measurements(self, sensor_id: int, start_date: datetime, end_date: datetime, min_value: float, max_value: float, page: int = 1, limit: int = 20) -> ListMeasurementsResponsePagination:
        rows, total_count, stats_min_value, stats_max_value, stats_average_value = self.measurement_repository.list_measurements(sensor_id=sensor_id, start_date=start_date, end_date=end_date, min_value=min_value, max_value=max_value, page=page, limit=limit)
        return ListMeasurementsResponsePagination(
            items=[MeasurementItem(
                id=row[0].measurementid,
                value=row[0].measurementvalue,
                timestamp=row[0].collectiontime,
                collectiontime=row[0].collectiontime,
                description=row[0].description,
                variabletype=row[0].variabletype,
                variablename=row[0].variablename,
                sensorid=row[0].sensorid,
                geometry=json.loads(row[1])
            ) for row in rows],
            total=total_count,
            page=page,
            size=limit,
            pages=total_count // limit + 1,
            min_value=stats_min_value,
            max_value=stats_max_value,
            average_value=stats_average_value
        )
