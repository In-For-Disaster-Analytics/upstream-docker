from typing import List, Optional

from pydantic import BaseModel

from app.api.v1.schemas.measurement import MeasurementIn


# Pydantic model for incoming sensor data
class SensorIn(BaseModel):
    alias: Optional[str | float] = None
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None
    variablename: str


class SensorItem(BaseModel):
    id: int
    alias: str | None = None
    description: str | None = None
    postprocess: bool | None = True
    postprocessscript: str | None = None
    units: str | None = None
    variablename: str | None = None


class ListSensorsResponse(SensorItem):
    pass

class GetSensorResponse(SensorItem):
    pass

# Pydantic model for incoming sensor and measurement data
class SensorAndMeasurementIn(BaseModel):
    sensor: SensorIn
    measurement: List[MeasurementIn]


class ListSensorsResponsePagination(BaseModel):
    items: list[SensorItem]
    total: int
    page: int
    size: int
    pages: int
