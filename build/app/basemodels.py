from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List

# Pydantic model for incoming location data
class LocationsIn(BaseModel):
    stationid: int
    collectiontime: datetime
    geometry : str

# Pydantic model for user data
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# Pydantic model for incoming campaign data
class CampaignsIn(BaseModel):
    campaignname:str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None
    allocation: str
    # # Validator for converting string to date for startdate
    # @validator("startdate", pre=True, allow_reuse=True)
    # def string_to_date(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
    #     return v
    # # Validator for converting string to date for enddate
    # @validator("enddate", pre=True, allow_reuse=True)
    # def string_to_date(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
    #     return v
    

# Pydantic model for outgoing campaign data
class CampaignsOut(BaseModel):
    campaignid: int
    campaignname: str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None
    # # Validator for converting string to date for startdate
    # @validator("startdate", pre=True, allow_reuse=True)
    # def string_to_date(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
    #     return v
    # # Validator for converting string to date for enddate
    # @validator("enddate", pre=True, allow_reuse=True)
    # def string_to_date(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
    #     return v
    
# Pydantic model for incoming station data
class StationIn(BaseModel):
    campaignid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime

    # @validator("startdate", pre=True, allow_reuse=True)
    # def string_to_date(cls, v: object) -> object:
    #     if isinstance(v, str):
    #         return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
    #     return v
    
  
# Pydantic model for outgoing station data
class StationOut(BaseModel):
    stationid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime

# Pydantic model for incoming measurement data
class MeasurementIn(BaseModel):
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    geometry : str

# Pydantic model for outgoing measurement data
class MeasurementOut(BaseModel):
    measurementid: int
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    location: LocationsIn

# Pydantic model for incoming sensor data
class SensorIn(BaseModel):
 
    alias: Optional[str] = None
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None

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

# Pydantic model for incoming sensor and measurement data
class SensorAndMeasurementIn(BaseModel):
    sensor: SensorIn
    measurement: List[MeasurementIn]
 

# Pydantic model for outgoing sensor and measurement data
class SensorAndMeasurementout(BaseModel):
    sensor: SensorOut
    measurement: List[MeasurementOut]
