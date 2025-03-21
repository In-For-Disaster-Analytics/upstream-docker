from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.api.v1.schemas.campaign import CampaignsIn
from app.db.models.campaign import (  # Adjust the import based on your model's location
    Campaign,
)
from app.db.models.station import Station
from app.db.models.sensor import Sensor


class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, request: CampaignsIn) -> Campaign:
        db_campaign = Campaign(
            campaignname=request.name,
            description=request.description,
            contactname=request.contact_name,
            contactemail=request.contact_email,
            allocation=request.allocation,
            startdate=request.start_date,
            enddate=request.end_date,
        )
        self.db.add(db_campaign)
        self.db.commit()
        self.db.refresh(db_campaign)
        return db_campaign

    def get_campaign(self, id: int) -> Campaign | None:
        campaign = self.db.query(Campaign).options(joinedload(Campaign.stations).joinedload(Station.sensors)).filter(Campaign.campaignid == id).first()
        for station in campaign.stations:
            station.geometry = self.db.scalar(func.ST_AsGeoJSON(station.geometry))
        return campaign

    def get_campaigns_and_summary(
        self,
        allocations: list[str] | None,
        bbox: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Campaign], int, int, list[str], list[str]]:
        # Base campaign query
        query = self.db.query(Campaign).options(joinedload(Campaign.stations).joinedload(Station.sensors))
        # Apply filters
        if allocations:
            query = query.filter(Campaign.allocation.in_(allocations))
        if bbox:
            bbox_west,bbox_south, bbox_east, bbox_north = bbox.split(",")
            query = query.filter(
                Campaign.bbox_west >= float(bbox_west),
                Campaign.bbox_east <= float(bbox_east),
                Campaign.bbox_south >= float(bbox_south),
                Campaign.bbox_north <= float(bbox_north),
            )
        if start_date:
            query = query.filter(Campaign.startdate >= start_date)
        if end_date:
            query = query.filter(Campaign.enddate <= end_date)

        total_count = self.db.query(Campaign).count()

        # Get paginated results
        campaings = query.offset((page - 1) * limit).limit(limit).all()

        sensor_types = []
        sensor_variables = []
        station_count = 0
        for campaign in campaings:
            station_count += len(campaign.stations)
            for station in campaign.stations:
                station.geometry = self.db.scalar(func.ST_AsGeoJSON(station.geometry))
                sensor_types.extend([sensor.alias for sensor in station.sensors])
                sensor_variables.extend([sensor.variablename for sensor in station.sensors])


        return campaings, total_count, station_count, sensor_types, sensor_variables

    def delete_campaign(self, campaign_id: int) -> bool:
        db_campaign = self.get_campaign(campaign_id)
        if db_campaign:
            self.db.delete(db_campaign)
            self.db.commit()
            return True
        return False

    def count_stations(self, campaign_id: int) -> int:
        return self.db.query(Station).filter(Station.campaignid == campaign_id).count()

    def count_sensors(self, campaign_id: int) -> int:
        stations = self.db.query(Station).filter(Station.campaignid == campaign_id).all()
        return sum(len(station.sensors) for station in stations)

    def get_sensor_types(self, campaign_id: int) -> list[str]:
        stations = self.db.query(Station).filter(Station.campaignid == campaign_id).all()
        return list(set(sensor.alias for station in stations for sensor in station.sensors))

    def get_sensor_variables(self, campaign_id: int) -> list[str]:
        stations = self.db.query(Station).filter(Station.campaignid == campaign_id).all()
        return list(set(sensor.variablename for station in stations for sensor in station.sensors))
