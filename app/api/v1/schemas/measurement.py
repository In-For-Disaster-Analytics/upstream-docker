from datetime import datetime
from typing import Optional, List

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
    sensorid: Optional[int] = None
    variablename: Optional[str] = None  # modified
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None


class MeasurementPagination(BaseModel):
    items: list[MeasurementItem]
    total: int
    page: int
    size: int
    pages: int
