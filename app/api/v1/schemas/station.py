from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


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

#__________________________MIO__________________________
class StationsListSummary(BaseModel):
    id: int 
    name: str
    sensors: List[dict] = Field(
        description="List of sensors in the station", 
        default=[],
        example=[
            {
                "id": 1,
                "variable_name": "Temperature",
                "measurement_unit": "Celsius"
            }
        ]
    )
