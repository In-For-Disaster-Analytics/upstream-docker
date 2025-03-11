
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.api.v1.utils.formatters import format_campaign
from app.api.v1.schemas.campaign import CampaignsOut, CampaignsIn
from app.api.v1.schemas.user import User
from app.db.models.campaign import Campaign
from app.db.models.campaignSensorType import CampaignSensorType
from app.db.session import SessionLocal
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.pytas import get_allocations
from app.api.v1.routes.campaigns.campaign_stations import router
from app.api.v1.schemas.locations import BoundingBoxFilter
router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Route for creating a new campaign, requires an authenticated user (current_user)
@router.post("", response_model=CampaignsOut)
async def post_campaign(campaign: CampaignsIn, current_user: User = Depends(get_current_user)):
    if campaign.dict()['allocation'] in get_allocations(current_user):
        with SessionLocal() as session:
            db_campaign = Campaign(**campaign.dict())
            session.add(db_campaign)
            session.commit()
            session.refresh(db_campaign)
            return CampaignsOut(**db_campaign.__dict__)
    else: raise HTTPException(status_code=404, detail="Allocation is incorrect")

@router.get("")
async def get_campaigns(
    bbox: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sensor_types: str | None = None,
    page: int | None = 1,
    limit: int | None = 20,
    current_user: User = Depends(get_current_user),
):
    with SessionLocal() as session:
        allocations = get_allocations(current_user)
        query = session.query(Campaign)
        # Filter the query by active allocations
        query = query.filter(Campaign.allocation.in_(allocations))

        # Apply filters
        if bbox:
            # Parse bbox parameter
            try:
                west, south, east, north = map(float, bbox.split(','))
                # Validate coordinates with Pydantic model
                BoundingBoxFilter(west=west, south=south, east=east, north=north)

                # Apply spatial filter
                query = query.filter(
                    Campaign.bbox_west <= east,
                    Campaign.bbox_east >= west,
                    Campaign.bbox_south <= north,
                    Campaign.bbox_north >= south
                )

            except ValidationError as exc:
                error_msgs = {
                    f"Error value for {err['loc'][0]}: {err['msg']}" for err in exc.errors()
                }
                raise HTTPException(status_code=400, detail=str(error_msgs))

            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Invalid bbox format")


        # Apply date filters
        if start_date:
            query = query.filter(Campaign.enddate >= start_date)

        if end_date:
            query = query.filter(Campaign.startdate <= end_date)

        #Apply sensor type filter
        if sensor_types:
            sensor_list = sensor_types.split(',')
            query = query.join(CampaignSensorType).filter(
                CampaignSensorType.sensor_type.in_(sensor_list)
            )

        # Count total results before pagination
        total_count = query.count()

        # Apply pagination
        paginated_query = query.offset((page - 1) * limit).limit(limit)

        # Execute query
        results = paginated_query.all()

         # Format response
        response = {
            "data": [format_campaign(c) for c in results],
            "metadata": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            }
        }

    return jsonable_encoder(response)

