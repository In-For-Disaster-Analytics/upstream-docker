from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from geoalchemy2 import Geometry
from datetime import datetime
from .config import settings


Base = declarative_base()



class Locations(Base):
    __tablename__ = "locations"
    locationid = Column(Integer, primary_key=True, index=True)
    stationid=Column(Integer)
    collectiontime = Column(DateTime, default=datetime.utcnow)
    geometry = Column(Geometry(geometry_type='POINT', srid=4326))


class Campaigns(Base):
    """
    Represents a campaign in the database.
    """
    __tablename__ = "campaigns"
    campaignid = Column(Integer, primary_key=True, index=True)
    campaignname = Column(String, unique=True)
    description = Column(String, nullable=True)
    contactname = Column(String, nullable=True)
    contactemail = Column(String, nullable=True)
    startdate = Column(DateTime)
    enddate = Column(DateTime, nullable=True)
    station = relationship("Station" , lazy="joined")
    allocation = Column(String, nullable=False)

class Sensor(Base):
    """
    Represents a sensor in the database.
    """
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

class Measurement(Base):
    """
    Represents a measurement in the database.
    """
    __tablename__ = "measurements"
    measurementid = Column(Integer, primary_key=True, index=True)
    sensorid = Column(Integer, ForeignKey('sensors.sensorid'))
    stationid = Column(Integer)
    variablename = Column(String)
    collectiontime = Column(DateTime)
    variabletype = Column(String, nullable=True)
    description = Column(String, nullable=True)
    measurementvalue = Column(Float, nullable=True)
    locationid = Column(Integer, ForeignKey('locations.locationid'))
    location = relationship("Locations", lazy="joined")

    # __mapper_args__ = {
    #     "primary_key": [Locations.stationid, Locations.collectiontime]
    # }
    
class SensorObject(Base):
    """
    Represents a sensor object in the database.
    """
    __tablename__ = "sensorobjects"
    objectid = Column(Integer, primary_key=True, index=True)
    sensorid = Column(Integer, ForeignKey('sensors.sensorid'), nullable=True)
    filename = Column(String)
    filetype = Column(String, nullable=True)
    filesize = Column(Float, nullable=True)
    creationdate = Column(DateTime)
    checksum = Column(String, nullable=True)



class Station(Base):
    """
    Represents a station in the database.
    """
    __tablename__ = "stations"
    stationid = Column(Integer, primary_key=True, index=True)
    campaignid = Column(Integer, ForeignKey('campaigns.campaignid'), nullable=True)
    stationname = Column(String, unique=True)
    projectid = Column(String, nullable=True)
    description = Column(String, nullable=True)
    contactname = Column(String, nullable=True)
    contactemail = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    startdate = Column(DateTime)
    sensor = relationship("Sensor", lazy="joined")
