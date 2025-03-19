from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.user import User
from app.db.session import get_db
from app.db.repositories.station_repository import StationRepository
from app.services.station_service import StationService
router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["stations"])


# Route to retrieve all stations associated with a specific campaign
@router.get("/stations")
async def list_stations(
    campaign_id: int, page: int = 1, limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    station_service = StationService(StationRepository(db))
    stations, total_count = station_service.get_stations_with_summary(campaign_id, page, limit)
    return jsonable_encoder(stations)

# Route to retrieve a specific station
@router.get("/stations/{station_id}")
async def get_station(station_id: int, campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    station_repository = StationRepository(db)
    station = station_repository.get_station(station_id)
    return station
