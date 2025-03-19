from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import check_allocation_permission, get_allocations
from app.api.v1.schemas.campaign import CampaignPagination, CampaignsIn, ListCampaignsResponseItem
from app.api.v1.schemas.user import User
from app.api.v1.utils.formatters import format_campaign
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.session import get_db


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("")
async def list_campaigns(
    page: int = 1,
    limit: int = 20,
    bbox: Annotated[str , Query(description="Bounding box of the campaign west,south,east,north")] = '-180,-90,180,90',
    start_date: Annotated[datetime | None, Query(description="Start date of the campaign", example="2024-01-01")] = None,
    end_date: Annotated[datetime | None, Query(description="End date of the campaign", example="2025-01-01")] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CampaignPagination:
    allocations = get_allocations(current_user)
    campaign_repository = CampaignRepository(db)
    results, total_count = campaign_repository.get_campaigns(
        allocations, bbox, start_date, end_date, page, limit
    )
    response = CampaignPagination(
        items=[format_campaign(c) for c in results],
        total=total_count,
        page=page,
        size=limit,
        pages=(total_count + limit - 1) // limit,
    )

    return jsonable_encoder(response)

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    campaign_repository = CampaignRepository(db)
    campaign = campaign_repository.get_campaign(campaign_id)
    return campaign