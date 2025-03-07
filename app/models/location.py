from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ..db.base import Base

class Locations(Base):
    __tablename__ = "locations"

    locationid = Column(Integer, primary_key=True, index=True)
    stationid = Column(Integer, ForeignKey("stations.stationid"))
    collectiontime = Column(DateTime)
    geometry = Column(Geometry('POINT', srid=4326))

    # Relationships
    station = relationship("Station", back_populates="locations")
    measurement = relationship("Measurement", back_populates="location")