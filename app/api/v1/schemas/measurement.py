from datetime import datetime
from typing import Optional, List

from geoalchemy2 import Geometry
from geojson_pydantic import Point
from pydantic import BaseModel


# Pydantic model for incoming measurement data
class MeasurementIn(BaseModel):
    sensorid: Optional[int] = None
    collectiontime: datetime
    geometry: str
    measurementvalue: float
    variablename: Optional[str] = None  # modified
    variabletype: Optional[str] = None
    description: Optional[str] = None


# Pydantic model for outgoing measurement data
class MeasurementItem(BaseModel):
    id: int
    value: float
    geometry: Point
    collectiontime: datetime
    sensorid: int | None = None
    variablename: str | None = None  # modified
    variabletype: str | None = None
    description: str | None = None

class ListMeasurementsResponsePagination(BaseModel):
    items: list[MeasurementItem]
    total: int
    page: int
    size: int
    pages: int
    min_value: float
    max_value: float
    average_value: float
    downsampled: bool
    downsampled_total: int | None = None

class AggregatedMeasurement(BaseModel):
    measurement_time: datetime
    value: float
    median_value: float
    point_count: int
    lower_bound: float
    upper_bound: float
    parametric_lower_bound: float
    parametric_upper_bound: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_25: float
    percentile_75: float
    ci_method: str
    confidence_level: float

    class Config:
        from_attributes = True