from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
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
    # relationships
    sensor: Mapped["Sensor"] = relationship(
        back_populates="measurements", lazy="joined"
    )
    geometry: Mapped[Geometry] = mapped_column(Geometry("POINT", srid=4326))
    upload_file_events_id: Mapped[int] = mapped_column(
        ForeignKey("upload_file_events.id", ondelete="CASCADE")
    )
    upload_file_event: Mapped["UploadFileEvent"] = relationship(lazy="joined") #  back_populates="measurements"

