from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.station import StationIn, StationOut
from app.api.v1.schemas.user import User
from app.db.models.station import Station
from app.db.session import SessionLocal, get_db
from app.db.repositories.station_repository import StationRepository

router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["campaign_stations"])


# Route to retrieve all stations associated with a specific campaign
@router.get("/stations")
async def read_station(
    campaign_id: int, current_user: User = Depends(get_current_user)
):
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            stations = (
                session.query(Station).filter(Station.campaignid == campaign_id).all()
            )
            return {
                "count": len(stations),
                "data": [StationOut(**station.__dict__) for station in stations],
            }

# Route to retrieve a specific station
@router.get("/stations/{station_id}")
async def get_station(station_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    station_repository = StationRepository(db)
    station = station_repository.get_station(station_id)
    return station

# Route to create a new station associated with a specific campaign
@router.post("/stations", response_model=StationOut)
async def post_station(
    station: StationIn,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
):
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            station.campaignid = campaign_id
            db_station = Station(**station.dict())
            session.add(db_station)
            session.commit()
            session.refresh(db_station)
            return StationOut(**db_station.__dict__)


# Route to update a station associated with a specific campaign
@router.patch("/stations/{station_id}", response_model=StationOut)
async def patch_station(
    station_id: int,
    station: StationIn,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
):
    if check_allocation_permission(current_user, campaign_id):
        with SessionLocal() as session:
            db_station = (
                session.query(Station).filter(Station.stationid == station_id).first()
            )
            if not db_station:
                raise HTTPException(status_code=404, detail="Station not found")
            station_data = station.dict(exclude_unset=True)
            for key, value in station_data.items():
                setattr(db_station, key, value)
            session.commit()
            session.refresh(db_station)
            return StationOut(**db_station.__dict__)

