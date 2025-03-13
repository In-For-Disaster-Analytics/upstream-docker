from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    contact_name: Optional[str]
    contact_email: Optional[str]


class CampaignResponse(BaseModel):
    items: list[CampaignsOut]
    total: int
    page: int
    size: int
    pages: int
