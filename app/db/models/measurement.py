from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"
    measurementid = Column(Integer, primary_key=True, index=True)
    sensorid = Column(Integer, ForeignKey("sensors.sensorid"))
    stationid = Column(Integer)
    variablename = Column(String)
    collectiontime = Column(DateTime)
    variabletype = Column(String, nullable=True)
    description = Column(String, nullable=True)
    measurementvalue = Column(Float, nullable=True)
    locationid = Column(Integer, ForeignKey("locations.locationid"))
    location = relationship("Locations", lazy="joined")
