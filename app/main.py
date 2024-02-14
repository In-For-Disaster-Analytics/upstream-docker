from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from geoalchemy2.elements import WKTElement
from typing import Optional, List, Annotated
from sqlalchemy.orm.exc import NoResultFound

from .basemodels import User, LocationsIn, CampaignsIn, CampaignsOut, StationIn, StationOut, MeasurementIn, MeasurementOut, SensorAndMeasurementIn, SensorAndMeasurementout, SensorIn, SensorOut
from .db import Campaigns, Locations, Sensor, Measurement, Station, Base
from .config import settings

from .pytas.http import TASClient
import jwt
from dotenv import load_dotenv

load_dotenv()
import os

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to create the database and tables based on the declared models

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# Event handler executed on application startup

@app.on_event("startup")
def startup():
        # Call the function to create the database and tables when the application starts
    create_db_and_tables()

# Event handler executed on application shutdown
@app.on_event("shutdown")
def shutdown():
    # Placeholder function for actions to be taken when the application is shutting down
    # (Currently, it does nothing as it is defined as pass)
    pass

# Function to authenticate a user by verifying the provided username and password
def authenticate_user(username, password):
     # Initialize a TASClient instance with the TAS server details and credentials

    client = TASClient(baseURL=os.getenv('tasURL'), credentials={'username':os.getenv('tasUser'), 'password':os.getenv('tasSecret')})
    return client.authenticate(username, password)

# Function to retrieve allocations (charge codes) associated with a given username
def get_allocations(username):
   
    client = TASClient(baseURL=os.getenv('tasURL'), credentials={'username':os.getenv('tasUser'), 'password':os.getenv('tasSecret')})
    return [u['chargeCode'] for u in client.projects_for_user(username=username)if u['allocations'][0]['status']!='Inactive']

# Async function to get the current user based on the provided OAuth2 token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_dict = unhash(token)
    user = authenticate_user(user_dict['username'], user_dict['password'])
    if not user:
            # If user authentication fails, raise an HTTPException with 401 UNAUTHORIZED status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Function to decode a JWT token using the specified secret and algorithm
def unhash(token):
    return jwt.decode(token, os.getenv('jwtSecret'), algorithms=[os.getenv('alg')])

# Function to encode a payload into a JWT token using the specified secret and algorithm
def hash(payload):
    return jwt.encode(payload, os.getenv('jwtSecret'), algorithm=os.getenv('alg'))

# Route for user authentication and token generation
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    authenticated = authenticate_user(form_data.username, form_data.password)

    if not authenticated:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(    get_allocations(form_data.username))
    user_dict = {'username':form_data.username, 'password':form_data.password}
    
    return {"access_token": hash(user_dict), "token_type": "bearer"}

# Route for creating a new campaign, requires an authenticated user (current_user)
@app.post("/campaign", response_model=CampaignsOut)
async def post_campaign(campaign: CampaignsIn, current_user: User = Depends(get_current_user)):
    with SessionLocal() as session:
        db_campaign = Campaigns(**campaign.dict())
        session.add(db_campaign)
        session.commit()
        session.refresh(db_campaign)
        return CampaignsOut(**db_campaign.__dict__)

# Route to retrieve all campaigns, requires an authenticated user (current_user)
@app.get("/campaign", response_model=List[CampaignsOut])
async def read_campaign(current_user: User = Depends(get_current_user)):
    with SessionLocal() as session:
        campaigns = session.query(Campaigns).all()
        print(campaigns)
        return [CampaignsOut(**campaign.__dict__) for campaign in campaigns]



# Route to retrieve all stations associated with a specific campaign
@app.get("/campaign/{campaign_id}/station")
async def read_station(campaign_id:int):
    with SessionLocal() as session:
        stations = session.query(Station).filter(Station.campaignid == campaign_id).all()
        return stations

# Route to create a new station associated with a specific campaign
@app.post("/campaign/{campaign_id}/station", response_model=StationOut)
async def post_station(station: StationIn, campaign_id:int):
    
    with SessionLocal() as session:
        station.campaignid= campaign_id
        db_station = Station(**station.dict())
        session.add(db_station)
        session.commit()
        session.refresh(db_station)
        return StationOut(**db_station.__dict__)

# Route to update a station associated with a specific campaign
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

# Route to retrieve all sensors associated with a specific station and campaign, with optional filtering parameters
@app.get("/campaign/{campaign_id}/station/{station_id}/sensor/")
async def get_sensors(
    station_id: int, 
    sensor_id: Optional[int]=None,
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    min_measurement_value: Optional[float] = None
):
    with SessionLocal() as session:
        db_sensor = session.query(Sensor).all()
    return db_sensor




# Route to retrieve sensor data based on specified parameters (e.g., sensor_id, date range, minimum measurement value)
@app.get("/campaign/{campaign_id}/station/{station_id}/sensor/{sensor_id}")
async def get_sensors(
    station_id: int, 
    sensor_id: int=None,
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None,
    min_measurement_value: Optional[float] = None
):
    with SessionLocal() as session:
        db_sensor = session.query(Sensor).filter(Sensor.sensorid == sensor_id).join(Sensor.measurement)

        if start_date:
            db_sensor = db_sensor.filter(Sensor.measurement.any(Measurement.collectiontime >= start_date))
        if end_date:
            db_sensor = db_sensor.filter(Sensor.measurement.any(Measurement.collectiontime <= end_date))
        if min_measurement_value is not None:
            db_sensor = db_sensor.filter(Measurement.measurementvalue > min_measurement_value)
        

        return  db_sensor.all()


# Route to create a new sensor and associated measurements for a specific station and campaign
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
       

        sensor = {key: getattr(db_sensor, key) for key in db_sensor.__table__.columns.keys()}

        return {"sensor":sensor, "measurement": db_measurements}
# Route to retrieve measurements with optional filtering based on the minimum measurement value
@app.get("/measurement")
async def read_measurement( min_measurement_value: Optional[float] = None
):
    with SessionLocal() as session:
        measurements = session.query(Measurement)
        if min_measurement_value is not None:
            measurements = measurements.filter(Measurement.measurementvalue > min_measurement_value)
        
        return measurements.all()
    

# Route to create a new measurement in the database
@app.post("/measurement", response_model=MeasurementOut)
async def post_measurement(measurement: MeasurementIn):
    with SessionLocal() as session:
        db_measurement = Measurement(**measurement.dict())
        session.add(db_measurement)
        session.commit()
        session.refresh(db_measurement)
        return db_measurement
