from app.api.v1.schemas.sensor import SensorItem
from app.api.v1.schemas.station import GetStationResponse
from app.db.repositories.station_repository import StationRepository


class StationService:
    def __init__(self, station_repository: StationRepository):
        self.station_repository = station_repository

    def get_stations_with_summary(self, campaign_id: int, page: int = 1, limit: int = 20) :
        rows, total_count = self.station_repository.list_stations_and_summary(campaign_id, page, limit)
        stations = []
        for row in rows:
            station = {
                "id": row[0].stationid,
                "name": row[0].stationname,
                "description": row[0].description,
                "sensor_types": row[2] or [],
                "sensor_variables": row[3] or [],
                "sensor_count": row[1]
            }
            stations.append(station)
        return stations, total_count


    def get_station(self, station_id: int) -> GetStationResponse | None:
        row = self.station_repository.get_station(station_id)
        if not row:
            return None
        return GetStationResponse(
            id=row.stationid,
            name=row.stationname,
            description=row.description,
            contact_name=row.contactname,
            contact_email=row.contactemail,
            active=row.active,
            start_date=row.startdate,
            sensors=[SensorItem(
                id=sensor.sensorid,
                alias=sensor.alias,
                description=sensor.description,
                postprocess=sensor.postprocess,
                variablename=sensor.variablename,
            ) for sensor in row.sensors]
        )
