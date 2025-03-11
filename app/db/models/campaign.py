from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    campaignid = Column(Integer, primary_key=True, index=True)
    campaignname = Column(String, unique=True)
    description = Column(String, nullable=True)
    contactname = Column(String, nullable=True)
    contactemail = Column(String, nullable=True)
    startdate = Column(DateTime)
    enddate = Column(DateTime, nullable=True)
    station = relationship("Station", lazy="joined")
    allocation = Column(String, nullable=False)
    bbox_west = Column(Float, nullable=True)
    bbox_east = Column(Float, nullable=True)
    bbox_south = Column(Float, nullable=True)
    bbox_north = Column(Float, nullable=True)
    sensor_types = relationship("CampaignSensorType", lazy="joined")

    def __repr__(self):
        return f"<Campaign(campaignname='{self.campaignname}')>"
