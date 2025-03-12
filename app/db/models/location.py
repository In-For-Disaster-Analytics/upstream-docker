from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from app.db.base import Base
from geoalchemy2 import Geometry

class Location(Base):
    __tablename__ = "locations"
    locationid: Mapped[int] = mapped_column(primary_key=True, index=True)
    stationid: Mapped[Optional[int]] = mapped_column(ForeignKey("stations.stationid"))
    collectiontime: Mapped[Optional[datetime]] = mapped_column()
    geometry: Mapped[Geometry] = mapped_column(Geometry("POINT", srid=4326)) 

    #relationships
    station: Mapped[Optional["Station"]] = relationship(back_populates="locations", lazy="joined")
    measurements: Mapped[List["Measurement"]] = relationship(back_populates="location", lazy="joined")

