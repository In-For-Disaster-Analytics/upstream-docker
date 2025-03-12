from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List, Optional
from datetime import datetime
from app.db.base import Base

class Station(Base):
    __tablename__ = "stations"

    stationid: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaignid: Mapped[int] = mapped_column(ForeignKey("campaigns.campaignid"), nullable=True)
    stationname: Mapped[str] = mapped_column(unique=True)
    projectid: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    contactname: Mapped[Optional[str]] = mapped_column()
    contactemail: Mapped[Optional[str]] = mapped_column()
    active: Mapped[Optional[bool]] = mapped_column()
    startdate: Mapped[Optional[datetime]] = mapped_column()
    
    #relationships
    campaigns: Mapped["Campaign"] = relationship(back_populates="stations", lazy="joined")
    sensors: Mapped[List["Sensor"]] = relationship(back_populates="station", lazy="joined")
    locations: Mapped[List["Location"]] = relationship(back_populates="station", lazy="joined")

