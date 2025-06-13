from app.services.campaign_service import CampaignService
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission
from app.api.v1.schemas.station import GetStationResponse, ListStationsResponsePagination, StationCreate, StationCreateResponse
from app.api.v1.schemas.user import User
from app.db.session import get_db
from app.db.repositories.station_repository import StationRepository
from app.db.repositories.campaign_repository import CampaignRepository
from app.services.station_service import StationService
router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["stations"])


@router.post("/stations")
async def create_station(station: StationCreate, campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StationCreateResponse:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    station_service = StationService(StationRepository(db))
    return station_service.create_station(station, campaign_id)

# Route to retrieve all stations associated with a specific campaign
@router.get("/stations")
async def list_stations(
    campaign_id: int, page: int = 1, limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ListStationsResponsePagination:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    station_service = StationService(StationRepository(db))
    stations, total_count = station_service.get_stations_with_summary(campaign_id, page, limit)
    return ListStationsResponsePagination(
        items=stations,
        total=total_count,
        page=page,
        size=limit,
        pages=total_count // limit + 1
    )

# Route to retrieve a specific station
@router.get("/stations/{station_id}")
async def get_station(station_id: int, campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GetStationResponse:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    station_service = StationService(StationRepository(db))
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.delete("/stations", status_code=204)
def delete_sensor(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if not check_allocation_permission(current_user, campaign_id):
        raise HTTPException(status_code=404, detail="Allocation is incorrect")
    campaign_repository = CampaignRepository(db)
    campaign_service = CampaignService(campaign_repository=campaign_repository)
    campaign_service.delete_campaign_station(campaign_id=campaign_id)
    return Response(status_code=204)