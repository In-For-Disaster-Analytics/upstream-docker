import os

from fastapi import HTTPException
from app.db.session import SessionLocal
from app.db.models.campaign import Campaign
from app.pytas.http import TASClient

# Function to retrieve allocations (charge codes) associated with a given username
def get_allocations(username):

    client = TASClient(baseURL=os.getenv('tasURL'), credentials={'username':os.getenv('tasUser'), 'password':os.getenv('tasSecret')})
    return [u['chargeCode'] for u in client.projects_for_user(username=username)if u['allocations'][0]['status']!='Inactive']


def check_allocation_permission(current_user, campaign_id):
    allocations = get_allocations(current_user)
    with SessionLocal() as session:
        allocations = get_allocations(current_user)
        db_allcation = session.query(Campaign).filter(Campaign.allocation.in_(allocations)).filter(Campaign.campaignid == campaign_id)
        if not db_allcation:
            raise HTTPException(status_code=404, detail="Access to Campaign unavailable. Improper Allocation")
        else: return True
