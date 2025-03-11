from typing import List, Optional

from pydantic import BaseModel

from app.api.v1.schemas.measurement import MeasurementIn, MeasurementOut


# Pydantic model for incoming sensor data
class SensorIn(BaseModel):
    alias: Optional[str] = None
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None
    variablename: str


# Pydantic model for outgoing sensor data
class SensorOut(BaseModel):
    sensorid: int
    stationid: int
    alias: str
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None
    measurements: List[MeasurementOut]
    variablename: str


# Pydantic model for incoming sensor and measurement data
class SensorAndMeasurementIn(BaseModel):
    sensor: SensorIn
    measurement: List[MeasurementIn]


# Pydantic model for outgoing sensor and measurement data
class SensorAndMeasurementout(BaseModel):
    sensor: SensorOut
    measurement: List[MeasurementOut]
