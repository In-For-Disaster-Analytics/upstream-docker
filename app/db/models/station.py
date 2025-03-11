from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Station(Base):
    __tablename__ = "stations"
    stationid = Column(Integer, primary_key=True, index=True)
    campaignid = Column(
        Integer, ForeignKey("campaigns.campaignid"), nullable=True
    )
    stationname = Column(String, unique=True)
    projectid = Column(String, nullable=True)
    description = Column(String, nullable=True)
    contactname = Column(String, nullable=True)
    contactemail = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    startdate = Column(DateTime)
    sensor = relationship("Sensor", lazy="joined")
    # location = relationship("Locations", lazy="joined")
