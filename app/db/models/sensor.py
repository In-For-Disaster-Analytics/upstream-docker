from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sensor(Base):
    __tablename__ = "sensors"

    sensorid = Column(Integer, primary_key=True, index=True)
    stationid = Column(Integer, ForeignKey("stations.stationid"), nullable=True)
    alias = Column(String, nullable=True)
    description = Column(String, nullable=True)
    postprocess = Column(Boolean, nullable=True)
    postprocessscript = Column(String, nullable=True)
    units = Column(String, nullable=True)
    variablename = Column(String, nullable=True)

    #relationships
    station = relationship("Station", lazy="joined")
    measurement = relationship("Measurement", lazy="joined")
    

