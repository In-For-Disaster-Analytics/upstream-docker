# app/main.py

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
from geoalchemy2.elements import WKTElement
from typing import Optional, List
from sqlalchemy.orm.exc import NoResultFound

from .db import Campaigns, Locations, Sensor, Measurement, Station, Base
from .config import settings

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(settings.db_url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI(title="FastAPI, Docker, and Traefik")


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    create_db_and_tables()

@app.on_event("shutdown")
def shutdown():
    pass


class CampaignsIn(BaseModel):
    campaignname:str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None

class CampaignsOut(BaseModel):
    campaignid: int
    campaignname: str
    contactname:Optional[str]
    contactemail:Optional[str]
    description: Optional[str] = None
    startdate: datetime
    enddate: Optional[datetime]=None


class StationIn(BaseModel):
    campaignid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime


class StationOut(BaseModel):
    stationid: Optional[int]
    stationname: str
    description: Optional[str] = None
    contactname: Optional[str] = None
    contactemail: Optional[str] = None
    active: Optional[bool] = True
    startdate: datetime


class SensorIn(BaseModel):
 
    alias: Optional[str] = None
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None



class SensorOut(BaseModel):
    sensorid: int
    stationid: int
    alias: str
    description: Optional[str] = None
    postprocess: Optional[bool] = True
    postprocessscript: Optional[str] = None
    units: Optional[str] = None



class MeasurementIn(BaseModel):
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None
    geometry : str

class MeasurementOut(BaseModel):
    measurementid: int
    sensorid: Optional[int] = None
    variablename: str
    collectiontime: datetime
    variabletype: Optional[str] = None
    description: Optional[str] = None
    measurementvalue: Optional[float] = None


class LocationsIn(BaseModel):
    stationid: int
    collectiontime: datetime
    geometry : str

class SensorAndMeasurementIn(BaseModel):
    sensor: SensorIn
    measurement: List[MeasurementIn]
 


class SensorAndMeasurementout(BaseModel):
    sensor: SensorOut
    measurement: List[MeasurementOut]

@app.post("/campaign", response_model=CampaignsOut)
async def post_campaign(campaign: CampaignsIn):
    with SessionLocal() as session:
        db_campaign = Campaigns(**campaign.dict())
        session.add(db_campaign)
        session.commit()
        session.refresh(db_campaign)
        return CampaignsOut(**db_campaign.__dict__)


@app.get("/campaign", response_model=List[CampaignsOut])
async def read_campaign():
    with SessionLocal() as session:
        campaigns = session.query(Campaigns).all()
        print(campaigns)
        return [CampaignsOut(**campaign.__dict__) for campaign in campaigns]




@app.get("/campaign/{campaign_id}/station")
async def read_station(campaign_id:int):
    with SessionLocal() as session:
        stations = session.query(Station).filter(Station.campaignid == campaign_id).all()
        return stations


@app.post("/campaign/{campaign_id}/station", response_model=StationOut)
async def post_station(station: StationIn, campaign_id:int):
    
    with SessionLocal() as session:
        station.campaignid= campaign_id
        db_station = Station(**station.dict())
        session.add(db_station)
        session.commit()
        session.refresh(db_station)
        return StationOut(**db_station.__dict__)


@app.patch("/campaign/{campaign_id}/station/{station_id}", response_model=StationOut)
async def patch_station(station_id: int, station: StationIn, campaign_id:int):
    with SessionLocal() as session:
        db_station = session.query(Station).filter(Station.stationid == station_id).first()
        if not db_station:
            raise HTTPException(status_code=404, detail="Station not found")
        station_data = station.dict(exclude_unset=True)
        for key, value in station_data.items():
            setattr(db_station, key, value)
        session.commit()
        session.refresh(db_station)
        return StationOut(**db_station.__dict__)


@app.get("/campaign/{campaign_id}/station/{station_id}/sensor")
async def read_sensor(campaign_id:int, station_id:int ):
    with SessionLocal() as session:
        sensors = session.query(Sensor).filter(Sensor.stationid == station_id).all()
        return sensors


@app.post("/campaign/{campaign_id}/station/{station_id}/sensor/", response_model=dict)
async def post_sensor_and_measurement(data: SensorAndMeasurementIn, station_id: int):
    sensor_data = data.sensor.dict()
    measurement_data_list = [measurement.dict() for measurement in data.measurement]

    with SessionLocal() as session:
        # Save sensor data
        
        sensor_data['stationid']=station_id

        db_sensor = Sensor(**sensor_data)
        session.add(db_sensor)
        session.commit()
        session.refresh(db_sensor)
        db_sensor = session.query(Sensor).filter(Sensor.sensorid == db_sensor.sensorid).first()

        if not db_sensor:
            raise HTTPException(status_code=500, detail="Failed to retrieve sensor data")
        # Save measurements with the associated sensor
        db_measurements = []
        location_data = {}
        for measurement_data in measurement_data_list:
            measurement_data['sensorid'] = db_sensor.sensorid
            location_data['geometry'] = measurement_data.pop('geometry', None)
            location_data['geometry'] = WKTElement(location_data['geometry'], srid=4326)
            location_data['stationid'] = station_id
            location_data['collectiontime']=measurement_data['collectiontime']
            db_measurement = Measurement(**measurement_data)
            session.add(db_measurement)
            try:
                # Try to find an existing location
                db_location = session.query(Locations).filter_by(
                    stationid=location_data['stationid'],
                    collectiontime=location_data['collectiontime'],
                    geometry=location_data['geometry'],
                ).one()

            except NoResultFound:
                # If no existing location is found, create a new one
                db_location = Locations(**location_data)
                session.add(db_location)
            
            session.commit()
            session.refresh(db_measurement)
            db_measurements.append(db_measurement.__dict__)
       
        # # Save locations with the associated sensor
        # db_locations = []
        # for location_data in measurement_data_list:
        #     location_data['location'] = WKTElement(location_data['location'], srid=4326)
        #     location_data['sensorid'] = db_sensor.sensorid
        #     db_location = locations(**location_data)
        #     session.add(db_location)
        #     session.commit()
        #     session.refresh(db_location)
        #     db_locations.append(db_location.__dict__)

        sensor = {key: getattr(db_sensor, key) for key in db_sensor.__table__.columns.keys()}

        return {"sensor":sensor, "measurement": db_measurements}

@app.get("/measurement")
async def read_measurement():
    with SessionLocal() as session:
        measurements = session.query(Measurement).all()
        return measurements
    


@app.post("/measurement", response_model=MeasurementOut)
async def post_measurement(measurement: MeasurementIn):
    with SessionLocal() as session:
        db_measurement = Measurement(**measurement.dict())
        session.add(db_measurement)
        session.commit()
        session.refresh(db_measurement)
        return db_measurement
