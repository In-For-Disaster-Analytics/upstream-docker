import os

from fastapi import HTTPException

from app.db.models.campaign import Campaign
from app.db.session import SessionLocal
from app.pytas.http import TASClient

ENVIRONMENT = os.getenv("ENVIRONMENT")


def get_allocations(username):
    if ENVIRONMENT == "dev":
        return ["test"]
    else:
        client = TASClient(
            baseURL=os.getenv("tasURL"),
            credentials={
                "username": os.getenv("tasUser"),
                "password": os.getenv("tasSecret"),
            },
        )
        return [
            u["chargeCode"]
            for u in client.projects_for_user(username=username)
            if u["allocations"][0]["status"] != "Inactive"
        ]


def check_allocation_permission(current_user, campaign_id):
    if ENVIRONMENT == "dev":
        return True
    else:
        allocations = get_allocations(current_user)
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
