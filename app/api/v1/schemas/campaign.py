from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CampaignsIn(BaseModel):
    campaignname:str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None
    allocation: str

class CampaignsOut(BaseModel):
    campaignid: int
    campaignname: str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None