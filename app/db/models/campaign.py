from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    campaignid = Column(Integer, primary_key=True, index=True)
    campaignname = Column(String, unique=True)
    description = Column(String, nullable=True)
    contactname = Column(String, nullable=True)
    contactemail = Column(String, nullable=True)
    startdate = Column(DateTime, nullable=True)
    enddate = Column(DateTime, nullable=True)
    allocation = Column(String, nullable=False)
    bbox_west = Column(Float, nullable=True)
    bbox_east = Column(Float, nullable=True)
    bbox_south = Column(Float, nullable=True)
    bbox_north = Column(Float, nullable=True)

    # Relationships
    stations = relationship("Station", back_populates="campaign")
    sensor_types = relationship("CampaignSensorType", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(campaignname='{self.campaignname}')>"

