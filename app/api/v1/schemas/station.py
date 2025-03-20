from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.api.v1.schemas.sensor import SensorItem


class StationIn(BaseModel):
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime


class StationItem(BaseModel):
    id: int
    name: str
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    active: bool | None = None
    start_date: datetime | None = None

class GetStationResponse(StationItem):
    sensors: List[SensorItem] | None = None

class ListStationPagination(BaseModel):
    items: List[StationItem]
    total: int
    page: int
    size: int
    pages: int

class SensorSummaryForStations(BaseModel):
    id: int
    variable_name: str | None = None
    measurement_unit: str | None = None

class StationsListResponseItem(StationItem):
    start_date: datetime
    sensors: List[SensorSummaryForStations] = []

class StationsPagination(BaseModel):
    items: List[StationsListResponseItem]
    total: int
    page: int
    size: int
    pages: int

