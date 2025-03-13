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

    # relationships
    campaign: Mapped["Campaign"] = relationship(
        back_populates="stations", lazy="joined"
    )
    sensors: Mapped[List["Sensor"]] = relationship(
        back_populates="station", lazy="joined"
    )
