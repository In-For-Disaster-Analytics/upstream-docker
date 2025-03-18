from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class StationIn(BaseModel):
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime


class StationOut(BaseModel):
    stationid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime

class StationPagination(BaseModel):
    items: List[StationOut]
    total: int
    page: int
    size: int
    pages: int

class SensorSummaryForStations(BaseModel):
    id: int
    variable_name: str | None = None
    measurement_unit: str | None = None
    
class StationsListResponseItem(BaseModel):
    id: int 
    name: str
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    active: bool | None = None
    start_date: datetime
    sensors: SensorSummaryForStations

class StationsPagination(BaseModel):
    items: List[StationsListResponseItem]
    total: int
    page: int
    size: int
    pages: int