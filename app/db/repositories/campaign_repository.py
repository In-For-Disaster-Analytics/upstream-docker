from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.campaign import CampaignsIn
from app.db.models.campaign import (  # Adjust the import based on your model's location
    Campaign,
)


class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, campaign: CampaignsIn) -> Campaign:
        db_campaign = Campaign(**campaign.dict())
        self.db.add(db_campaign)
        self.db.commit()
        self.db.refresh(db_campaign)
        return db_campaign

    def get_campaign(self, campaign_id: int) -> Campaign:
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def get_campaigns(
        self,
        allocations: list[str] | None,
        bbox: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Campaign], int]:
        query = self.db.query(Campaign)
        if allocations:
            query = query.filter(Campaign.allocation.in_(allocations))
        if bbox:
            query = query.filter(
                Campaign.bbox_west <= bbox[0],
                Campaign.bbox_east >= bbox[1],
                Campaign.bbox_south <= bbox[2],
                Campaign.bbox_north >= bbox[3],
            )
        if start_date:
            query = query.filter(Campaign.startdate >= start_date)
        if end_date:
            query = query.filter(Campaign.enddate <= end_date)
        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count

    def get_all_campaigns(self) -> list[Campaign]:
        return self.db.query(Campaign).all()

    # def update_campaign(self, campaign_id: int, campaign_data: CampaignUpdate) -> Campaign:
    #     db_campaign = self.get_campaign(campaign_id)
    #     if db_campaign:
    #         for key, value in campaign_data.dict(exclude_unset=True).items():
    #             setattr(db_campaign, key, value)
    #         self.db.commit()
    #         self.db.refresh(db_campaign)
    #     return db_campaign

    def delete_campaign(self, campaign_id: int) -> bool:
        db_campaign = self.get_campaign(campaign_id)
        if db_campaign:
            self.db.delete(db_campaign)
            self.db.commit()
            return True
        return False
