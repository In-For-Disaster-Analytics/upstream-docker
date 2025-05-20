from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SensorStatistics(Base):
    __tablename__ = 'sensor_statistics'

    sensorid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('sensors.sensorid', ondelete='CASCADE'),
        primary_key=True
    )
    max_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    min_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    avg_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    stddev_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    percentile_90: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    percentile_95: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    percentile_99: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_measurement_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    last_measurement_collectiontime: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    stats_last_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now
    )

    # Relationship with Sensor model
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="statistics")