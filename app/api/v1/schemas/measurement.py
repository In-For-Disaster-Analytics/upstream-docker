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
