from datetime import datetime
from typing import Optional, List

from geoalchemy2 import Geometry
from geojson_pydantic import Point
from pydantic import BaseModel


# Pydantic model for incoming measurement data
class MeasurementIn(BaseModel):
    sensorid: Optional[int] = None
    variablename: Optional[str] = None  # modified
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    geometry: str


# Pydantic model for outgoing measurement data
class MeasurementItem(BaseModel):
    id: int
    sensorid: int | None = None
    variablename: str | None = None  # modified
    collectiontime: datetime
    variabletype: str | None = None
    description: str | None = None
    value: float | None = None
    geometry: Point | None = None

class ListMeasurementsResponsePagination(BaseModel):
    items: list[MeasurementItem]
    total: int
    page: int
    size: int
    pages: int
    min_value: float
    max_value: float
    average_value: float
