from fastapi import HTTPException

from app.api.v1.schemas.user import User
from app.db.models.campaign import Campaign
from app.db.session import SessionLocal
from app.pytas.http import TASClient
from app.core.config import Settings, get_settings

settings = get_settings()

ENVIRONMENT = settings.ENV

dev_allocations = ["WEATHER-456", "WEATHER-457", "WEATHER-458", "TEST-123", "string"]

def get_allocations(username: str) -> list[str]:
    if ENVIRONMENT == "dev":
        return dev_allocations
    else:
        client = TASClient(
            baseURL=settings.tasURL,
            credentials={
                "username": settings.tasUser,
                "password": settings.tasSecret,
            },
        )
        return [
            u.chargeCode
            for u in client.projects_for_user(username=username)
            if u.allocations[0].status != "Inactive"
        ]


def check_allocation_permission(current_user: User, campaign_id: int) -> bool:
    if ENVIRONMENT == "dev":
        return True
    else:
        allocations = get_allocations(current_user.username)
        with SessionLocal() as session:
            db_allcation = (
                session.query(Campaign)
                .filter(Campaign.allocation.in_(allocations))
                .filter(Campaign.campaignid == campaign_id)
            )
        if not db_allcation:
            raise HTTPException(
                status_code=404,
                detail="Access to Campaign unavailable. Improper Allocation",
            )
        else:
            return True

