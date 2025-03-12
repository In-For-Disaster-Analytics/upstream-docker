from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    measurementid = Column(Integer, primary_key=True, index=True)
    sensorid = Column(Integer, ForeignKey("sensors.sensorid"), nullable=True)
    stationid = Column(Integer, nullable=True)
    variablename = Column(String, nullable=True)
    collectiontime = Column(DateTime, nullable=True)
    variabletype = Column(String, nullable=True)
    description = Column(String, nullable=True)
    measurementvalue = Column(Float, nullable=True)
    locationid = Column(Integer, ForeignKey("locations.locationid"), nullable=True)

    #relationships
    location = relationship("Location", lazy="joined")
