from datetime import datetime
from typing import List

from pydantic import BaseModel


class CampaignsIn(BaseModel):
    name: str
    contact_name: str | None = None
    contact_email: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    allocation: str

class Location(BaseModel):
    bbox_west: float | None = None
    bbox_east: float | None = None
    bbox_south: float | None = None
    bbox_north: float | None = None

class SummaryListCampaigns(BaseModel):
    sensor_types: List[str] | None = None
    variable_names: List[str] | None = None

class ListCampaignsResponseItem(BaseModel):
    id: int
    name: str
    location: Location | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    allocation: str | None = None
    summary: SummaryListCampaigns

class CampaignPagination(BaseModel):
    items: list[ListCampaignsResponseItem]
    total: int
    page: int
    size: int
    pages: int

class SummaryGetCampaign(BaseModel):
    station_count: int
    sensor_count: int
    sensor_types: List[str]
    sensor_variables: List[str]

class GetCampaignResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    allocation: str
    location: Location | None = None
    summary: SummaryGetCampaign
