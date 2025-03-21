from datetime import datetime
import json
from app.api.v1.schemas.station import SensorSummaryForStations, StationsListResponseItem
from app.db.repositories.campaign_repository import CampaignRepository
from app.api.v1.schemas.campaign import GetCampaignResponse, ListCampaignsResponseItem, Location, SummaryGetCampaign, SummaryListCampaigns

class CampaignService:
    def __init__(self, campaign_repository: CampaignRepository):
        self.campaign_repository = campaign_repository

    def get_campaigns_with_summary(
        self,
        allocations: list[str] | None = None,
        bbox: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ListCampaignsResponseItem], int]:
        rows, total_count, station_count, sensor_types, sensor_variables = self.campaign_repository.get_campaigns_and_summary(
            allocations, bbox, start_date, end_date, page, limit
        )
        items: list[ListCampaignsResponseItem] = []
        for row in rows:
            item = ListCampaignsResponseItem(
                id=row.campaignid,
                name=row.campaignname,
                description=row.description,
                contact_name=row.contactname,
                contact_email=row.contactemail,
                start_date=row.startdate,
                end_date=row.enddate,
                allocation=row.allocation,
                location=Location(
                    bbox_west=row.bbox_west,
                    bbox_east=row.bbox_east,
                    bbox_south=row.bbox_south,
                    bbox_north=row.bbox_north,
                ),
                summary=SummaryListCampaigns(
                    sensor_types=sensor_types,
                    variable_names=sensor_variables
                )
            )
            items.append(item)
        return items, total_count

    def get_campaign_with_summary(self, campaign_id: int) -> GetCampaignResponse | None:
        campaign = self.campaign_repository.get_campaign(campaign_id)
        if not campaign:
            return None
        stations = [StationsListResponseItem(
            id=station.stationid,
            name=station.stationname,
            description=station.description,
            contact_name=station.contactname,
            contact_email=station.contactemail,
            active=station.active,
            start_date=station.startdate,
            geometry=json.loads(station.geometry) if station.geometry else None,
            sensors=[SensorSummaryForStations(
                id=sensor.sensorid,
                variable_name=sensor.variablename,
                measurement_unit=sensor.units,
            ) for sensor in station.sensors]
        ) for station in campaign.stations]
        return GetCampaignResponse(
            id=campaign.campaignid,
            name=campaign.campaignname,
            description=campaign.description,
            contact_name=campaign.contactname,
            contact_email=campaign.contactemail,
            start_date=campaign.startdate,
            end_date=campaign.enddate,
            allocation=campaign.allocation,
            location=Location(
                bbox_west=campaign.bbox_west,
                bbox_east=campaign.bbox_east,
                bbox_south=campaign.bbox_south,
                bbox_north=campaign.bbox_north,
            ),
            stations=stations,
            summary=SummaryGetCampaign(
                station_count=self.campaign_repository.count_stations(campaign_id),
                sensor_count=self.campaign_repository.count_sensors(campaign_id),
                sensor_types=self.campaign_repository.get_sensor_types(campaign_id),
                sensor_variables=self.campaign_repository.get_sensor_variables(campaign_id),
            ),
        )

