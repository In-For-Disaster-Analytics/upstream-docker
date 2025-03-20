from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Station(Base):
    __tablename__ = "stations"

    stationid: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaignid: Mapped[int] = mapped_column(
        ForeignKey("campaigns.campaignid"), nullable=True
    )
    stationname: Mapped[str] = mapped_column(unique=True)
    projectid: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    contactname: Mapped[Optional[str]] = mapped_column()
    contactemail: Mapped[Optional[str]] = mapped_column()
    active: Mapped[Optional[bool]] = mapped_column()
    startdate: Mapped[Optional[datetime]] = mapped_column()

    # Station type
    station_type: Mapped[str] = mapped_column()  # 'static' or 'mobile'

    # Location for static stations
    static_latitude: Mapped[Optional[float]] = mapped_column()
    static_longitude: Mapped[Optional[float]] = mapped_column()

    # Bounding box coordinates for mobile stations
    mobile_bbox_west: Mapped[Optional[float]] = mapped_column()
    mobile_bbox_east: Mapped[Optional[float]] = mapped_column()
    mobile_bbox_south: Mapped[Optional[float]] = mapped_column()
    mobile_bbox_north: Mapped[Optional[float]] = mapped_column()

    # relationships
    campaign: Mapped["Campaign"] = relationship(
        back_populates="stations"
    )
    sensors: Mapped[List["Sensor"]] = relationship(
        back_populates="station"
    )
