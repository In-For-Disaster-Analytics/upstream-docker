from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CampaignsIn(BaseModel):
    name: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    description: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    allocation: str


class CampaignsOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    

class CampaignPagination(BaseModel):
    items: list[CampaignsOut]
    total: int
    page: int
    size: int
    pages: int

#__________________________MIO__________________________
class CampaignListSummary(BaseModel):
    id: int
    name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    location: dict | None = None
    summary: dict = Field(description="Summary information about the campaigns", default={
        "sensor_types": [],
        "variable_names": []
    })

class CampaignListSummary(BaseModel):
    id: int
    name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    location: dict | None = None
    summary: dict = Field(description="Summary information about the campaigns", default={
        "sensor_types": [],
        "variable_names": []
    })

    