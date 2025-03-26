from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.api.v1.schemas.station import StationCreate
from app.db.models.sensor import Sensor
from app.db.models.station import Station


class StationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_station(self, request: StationCreate, campaign_id: int) -> Station:
        db_station = Station(
            stationname=request.name,
            description=request.description,
            contactname=request.contact_name,
            contactemail=request.contact_email,
            active=request.active,
            startdate=request.start_date,
            campaignid=campaign_id,
            station_type=request.station_type.value
        )
        self.db.add(db_station)
        self.db.commit()
        self.db.refresh(db_station)
        return db_station

    def get_station(self, station_id: int) -> Station | None:
        station = self.db.query(Station)\
            .options(joinedload(Station.sensors))\
            .add_columns(func.ST_AsGeoJSON(Station.geometry).label('geometry_str'))\
            .filter(Station.stationid == station_id)\
            .first()

        if station:
            station[0].geometry = station[1]  # Replace geometry with string version
            return station[0]
        return None

    def get_stations_by_campaign_id(self, campaign_id: int, page: int = 1, limit: int = 20) -> list[Station]:
        return self.db.query(Station).filter(Station.campaignid == campaign_id).offset((page - 1) * limit).limit(limit).all()

    def list_stations_and_summary(self, campaign_id: int, page: int = 1, limit: int = 20) -> tuple[list[tuple[Station, int, list[str], list[str], str]], int]:
        query = self.db.query(Station,
            func.count(Sensor.sensorid.distinct()).label('sensor_count'),
            func.array_agg(func.distinct(Sensor.alias)).label('sensor_types'),
            func.array_agg(func.distinct(Sensor.variablename)).label('sensor_variables'),
            func.ST_AsGeoJSON(Station.geometry).label('geometry')
        ).select_from(Station).outerjoin(Sensor).filter(Station.campaignid == campaign_id).group_by(Station.stationid)

        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count

    def get_stations(
        self,
        campaign_id: Optional[int] = None,
        active: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Station], int]:
        query = self.db.query(Station)
        if campaign_id:
            query = query.filter(Station.campaignid == campaign_id)
        if active is not None:
            query = query.filter(Station.active == active)
        if start_date:
            query = query.filter(Station.startdate >= start_date)

        total_count = query.count()
        return query.offset((page - 1) * limit).limit(limit).all(), total_count

    def delete_station(self, station_id: int) -> bool:
        db_station = self.get_station(station_id)
        if db_station:
            self.db.delete(db_station)
            self.db.commit()
            return True
        return False
