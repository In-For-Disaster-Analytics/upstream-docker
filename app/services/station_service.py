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


    def get_station_with_summary(self, station_id: int) -> dict | None:
        row = self.station_repository.get_station(station_id)
        if not row:
            return None
        return {
            "id": row.stationid,
            "name": row.stationname,
            "description": row.description,
        }
