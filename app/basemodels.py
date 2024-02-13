from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List


class LocationsIn(BaseModel):
    stationid: int
    collectiontime: datetime
    geometry : str

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class CampaignsIn(BaseModel):
    campaignname:str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None
    allocation: str

    @validator("startdate", pre=True, allow_reuse=True)
    def string_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%b-%Y").date()
        return v
    
    @validator("enddate", pre=True, allow_reuse=True)
    def string_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%b-%Y").date()
        return v

class CampaignsOut(BaseModel):
    campaignid: int
    campaignname: str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None

    @validator("startdate", pre=True, allow_reuse=True)
    def string_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%b-%Y").date()
        return v
    
    @validator("enddate", pre=True, allow_reuse=True)
    def string_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%b-%Y").date()
        return v

class StationIn(BaseModel):
    campaignid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime

    @validator("startdate", pre=True, allow_reuse=True)
    def string_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%b-%Y").date()
        return v
    
  

class StationOut(BaseModel):
    stationid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime


class MeasurementIn(BaseModel):
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    geometry : str

class MeasurementOut(BaseModel):
    measurementid: int
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    location: LocationsIn

class SensorIn(BaseModel):
 
    alias: Optional[str] = None
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None

class SensorOut(BaseModel):
    sensorid: int
    stationid: int
    alias: str
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None
    measurements: List[MeasurementOut]


class SensorAndMeasurementIn(BaseModel):
    sensor: SensorIn
    measurement: List[MeasurementIn]
 


class SensorAndMeasurementout(BaseModel):
    sensor: SensorOut
    measurement: List[MeasurementOut]
