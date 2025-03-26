from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select, or_
from geoalchemy2.functions import ST_AsGeoJSON # Add this import at the top

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
        result = (
            self.db.query(Campaign, ST_AsGeoJSON(Campaign.geometry).label('geometry'))
            .options(
                joinedload(Campaign.stations).joinedload(Station.sensors),
            )
            .filter(Campaign.campaignid == id)
            .first()
        )
        campaign = result[0]
        geometry = result[1]
        if campaign:
            campaign.geometry = geometry
            print("campaign", campaign.geometry)
            for station in campaign.stations:
                if station.geometry:
                    # Convert each station's geometry to string
                    station.geometry = self.db.scalar(
                        ST_AsGeoJSON(Station.geometry)
                    )

        return campaign

    def get_campaigns_and_summary(
        self,
        allocations: list[str] | None,
        bbox: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[tuple[Campaign, int, int, list[str], list[str]]], int]:
        # Base campaign query
        query = self.db.query(
            Campaign,
            func.count(Station.stationid.distinct()).label('station_count'),
            func.count(Sensor.sensorid.distinct()).label('sensor_count'),
            func.array_agg(func.distinct(Sensor.alias)).label('sensor_types'),
            func.array_agg(func.distinct(Sensor.variablename)).label('sensor_variables'),
            ST_AsGeoJSON(Campaign.geometry).label('geometry')
        ).select_from(Campaign).outerjoin(Station).outerjoin(Station.sensors).group_by(Campaign.campaignid)

        print("query", allocations, bbox, start_date, end_date)
        # Apply filters
        if allocations:
            query = query.filter(Campaign.allocation.in_(allocations))
        if bbox:
            print("bbox", bbox)
            bbox_north, bbox_east, bbox_south, bbox_west = bbox.split(",")
            query = query.filter(
                func.ST_Intersects(
                    Campaign.geometry,
                    func.ST_MakeEnvelope(
                        float(bbox_west),
                        float(bbox_south),
                        float(bbox_east),
                        float(bbox_north),
                        4326  # SRID for WGS84
                    )
                )
            )
        if start_date:
            query = query.filter(
                or_(
                    Campaign.startdate.is_(None),
                    Campaign.startdate >= start_date
                )
            )
        if end_date:
            query = query.filter(
                or_(
                    Campaign.enddate.is_(None),
                    Campaign.enddate <= end_date
                )
            )

        total_count = self.db.query(Campaign).count()

        # Get paginated results
        results = query.offset((page - 1) * limit).limit(limit).all()

        return results, total_count

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

    def list_stations_and_summary(self, campaign_id: int, page: int = 1, limit: int = 20) -> tuple[list[tuple[Station, int, list[str], list[str]]], int]:
        query = self.db.query(
            Station,
            func.count(Sensor.sensorid.distinct()).label('sensor_count'),
            func.array_agg(func.distinct(Sensor.alias)).label('sensor_types'),
            func.array_agg(func.distinct(Sensor.variablename)).label('sensor_variables'),
            ST_AsGeoJSON(Station.geometry).label('geometry')
        ).select_from(Station).outerjoin(Sensor).filter(
            Station.campaignid == campaign_id
        ).group_by(Station.stationid)

        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count
