from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Sensor(Base):
    __tablename__ = "sensors"
    sensorid = Column(Integer, primary_key=True, index=True)
    stationid = Column(Integer, ForeignKey('stations.stationid'))
    alias = Column(String)
    description = Column(String, nullable=True)
    postprocess = Column(Boolean, default=True)
    postprocessscript = Column(String, nullable=True)
    units = Column(String, nullable=True)
    measurement = relationship("Measurement" , lazy="joined")
    station  = relationship("Station" , lazy="joined")
    variablename = Column(String)
