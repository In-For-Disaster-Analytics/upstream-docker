from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base

class Station(Base):
    __tablename__ = "stations"

    stationid = Column(Integer, primary_key=True, index=True)
    stationname = Column(String)
    description = Column(String)
    campaignid = Column(Integer, ForeignKey("campaigns.campaignid"))

    # Relationships
    campaign = relationship("Campaigns", back_populates="station")
    sensor = relationship("Sensor", back_populates="station")
    locations = relationship("Locations", back_populates="station")