from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StationIn(BaseModel):
    campaignid: Optional[int]
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
