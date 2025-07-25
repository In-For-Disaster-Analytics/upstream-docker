from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.api.v1.schemas.station import StationsListResponseItem


class CampaignsIn(BaseModel):
    name: str
    contact_name: str | None = None
    contact_email: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    allocation: str

class CampaignCreateResponse(BaseModel):
    id: int

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
    geometry: dict = Field(default_factory=dict, nullable=True)  # type: ignore[call-overload,type-arg]

class ListCampaignsResponsePagination(BaseModel):
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
    geometry: dict = Field(default_factory=dict, nullable=True)  # type: ignore[call-overload,type-arg]
    stations: list[StationsListResponseItem] = []


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    allocation: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None