from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Sensor(Base):
    __tablename__ = "sensors"

    sensorid = Column(Integer, primary_key=True, index=True)
    sensorname = Column(String)
    description = Column(String)
    sensortype = Column(String)
    units = Column(String)
    stationid = Column(Integer, ForeignKey("stations.stationid"))

    # Relationships
    station = relationship("Station", back_populates="sensor")
    measurement = relationship("Measurement", back_populates="sensor")