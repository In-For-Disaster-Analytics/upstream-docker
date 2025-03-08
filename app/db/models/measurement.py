from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Measurement(Base):
    __tablename__ = "measurements"

    measurementid = Column(Integer, primary_key=True, index=True)
    sensorid = Column(Integer, ForeignKey("sensors.sensorid"))
    locationid = Column(Integer, ForeignKey("locations.locationid"))
    measurementvalue = Column(Float)
    collectiontime = Column(DateTime)

    # Relationships
    sensor = relationship("Sensor", back_populates="measurement")
    location = relationship("Locations", back_populates="measurement")