from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CampaignsIn(BaseModel):
    campaignname: str
    contactname: Optional[str]
    contactemail: Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime] = None
    allocation: str


class CampaignsOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    contact_name: Optional[str]
    contact_email: Optional[str]


class CampaignResponse(BaseModel):
    items: list[CampaignsOut]
    total: int
    page: int
    size: int
    pages: int
