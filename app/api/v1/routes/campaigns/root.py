from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import get_allocations
from app.api.v1.schemas.campaign import CampaignResponse, CampaignsIn, CampaignsOut
from app.api.v1.schemas.user import User
from app.api.v1.utils.formatters import format_campaign
from app.db.models.campaign import Campaign
from app.db.repositories.campaign_repository import CampaignRepository
from app.db.session import SessionLocal

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignsOut)
async def post_campaign(
    campaign: CampaignsIn, current_user: User = Depends(get_current_user)
):
    if campaign.dict()["allocation"] in get_allocations(current_user):
        with SessionLocal() as session:
            db_campaign = Campaign(**campaign.dict())
            session.add(db_campaign)
            session.commit()
            session.refresh(db_campaign)
            return CampaignsOut(**db_campaign.__dict__)
    else:
        raise HTTPException(status_code=404, detail="Allocation is incorrect")


@router.get("")
async def get_campaigns(
    bbox: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
) -> CampaignResponse:
    allocations = get_allocations(current_user)
    with SessionLocal() as session:
        campaign_repository = CampaignRepository(session)
        results, total_count = campaign_repository.get_campaigns(
            allocations, bbox, start_date, end_date, page, limit
        )
        # Format response
        response = CampaignResponse(
            items=[format_campaign(c) for c in results],
            total=total_count,
            page=page,
            size=limit,
            pages=(total_count + limit - 1) // limit,
        )

    return jsonable_encoder(response)
