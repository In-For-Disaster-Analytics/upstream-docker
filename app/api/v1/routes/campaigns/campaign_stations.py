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
async def list_stations(
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
