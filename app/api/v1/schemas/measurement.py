from datetime import datetime
from typing import Optional

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
class MeasurementOut(BaseModel):
    measurementid: int
    sensorid: Optional[int] = None
    variablename: Optional[str] = None  # modified
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    location: LocationsIn
