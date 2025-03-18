from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    campaignid: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaignname: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    contactname: Mapped[Optional[str]] = mapped_column()
    contactemail: Mapped[Optional[str]] = mapped_column()
    startdate: Mapped[Optional[datetime]] = mapped_column()
    enddate: Mapped[Optional[datetime]] = mapped_column()
    allocation: Mapped[str] = mapped_column()
    bbox_west: Mapped[Optional[float]] = mapped_column()
    bbox_east: Mapped[Optional[float]] = mapped_column()
    bbox_south: Mapped[Optional[float]] = mapped_column()
    bbox_north: Mapped[Optional[float]] = mapped_column()

    @property
    def location(self) -> dict:
        if all(coord is not None for coord in [self.bbox_west, self.bbox_east, self.bbox_south, self.bbox_north]):
            return {
                "west": self.bbox_west,
                "east": self.bbox_east,
                "south": self.bbox_south,
                "north": self.bbox_north
            }
        return {}
    
    # relationships
    stations: Mapped[List["Station"]] = relationship(
        back_populates="campaign"
    )