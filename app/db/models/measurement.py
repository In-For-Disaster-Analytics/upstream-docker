from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    measurementid: Mapped[int] = mapped_column(primary_key=True, index=True)
    sensorid: Mapped[int] = mapped_column(ForeignKey("sensors.sensorid"))
    stationid: Mapped[int] = mapped_column()
    variablename: Mapped[Optional[str]] = mapped_column()
    collectiontime: Mapped[Optional[datetime]] = mapped_column()
    variabletype: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    measurementvalue: Mapped[Optional[float]] = mapped_column()
    # locationid: Mapped[int] = mapped_column(ForeignKey("locations.locationid"))

    # relationships
    sensor: Mapped["Sensor"] = relationship(
        back_populates="measurements", lazy="joined"
    )
    # locations: Mapped["Location"] = relationship(back_populates="measurements", lazy="joined")
