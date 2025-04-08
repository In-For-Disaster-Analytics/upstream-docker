from datetime import datetime
import json
from app.api.v1.schemas.measurement import AggregatedMeasurement, MeasurementItem, ListMeasurementsResponsePagination
from app.db.repositories.measurement_repository import MeasurementRepository
from app.utils.lttb import lttb


class MeasurementService:
    def __init__(self, measurement_repository: MeasurementRepository):
        self.measurement_repository = measurement_repository

    def list_measurements(self, sensor_id: int, start_date: datetime | None, end_date: datetime | None, min_value: float | None, max_value: float | None, page: int = 1, limit: int = 20, downsample_threshold: int | None = None) -> ListMeasurementsResponsePagination:
        rows, total_count, stats_min_value, stats_max_value, stats_average_value = self.measurement_repository.list_measurements(sensor_id=sensor_id, start_date=start_date, end_date=end_date, min_value=min_value, max_value=max_value, page=page, limit=limit)

        # Convert rows to MeasurementItem objects
        measurements : list[MeasurementItem] = []
        for row in rows:
            if row[1] is not None:
                measurements.append(MeasurementItem(
                    id=row[0].measurementid,
                    value=row[0].measurementvalue,
                    collectiontime=row[0].collectiontime,
                    description=row[0].description,
                    variabletype=row[0].variabletype,
                    variablename=row[0].variablename,
                    sensorid=row[0].sensorid,
                    geometry=json.loads(row[1])
                ))
            else:
                print(f"Measurement {row[0].measurementid} has no geometry {row[1]}")

        # Apply LTTB downsampling if threshold is provided
        if downsample_threshold is not None and downsample_threshold > 2:
            measurements = lttb(measurements, downsample_threshold)

        return ListMeasurementsResponsePagination(
            items=measurements,
            total=total_count,
            page=page,
            size=limit,
            pages=total_count // limit + 1,
            min_value=stats_min_value if stats_min_value is not None else 0,
            max_value=stats_max_value if stats_max_value is not None else 0,
            average_value=stats_average_value if stats_average_value is not None else 0
        )

    def get_measurements_with_confidence_intervals(self, sensor_id: int, interval: str, interval_value: int, start_date: datetime | None, end_date: datetime | None, min_value: float | None, max_value: float | None) -> list[AggregatedMeasurement]:
        return self.measurement_repository.get_measurements_with_confidence_intervals(sensor_id=sensor_id, interval=interval, interval_value=interval_value, start_date=start_date, end_date=end_date, min_value=min_value, max_value=max_value)