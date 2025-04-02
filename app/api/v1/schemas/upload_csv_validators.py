from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, field_validator
from dateutil.parser import parse


class SensorCSV(BaseModel):
    alias: str
    variablename: str | None = Field(alias='BestGuessFormula', default=None)
    postprocess: bool = True
    postprocessscript: str | None = None
    description: str | None = None
    units: str | None = None

class CollTimeCSV(BaseModel):
    collection_time: datetime

    @field_validator('collection_time', mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            try:
                return parse(value)
            except Exception as ex:
                raise ValueError (str(ex))
        return value

class LocationCSV(BaseModel):
    long_deg: float
    lat_deg: float

class MeasurementCSV(BaseModel):
    measurement_value: float