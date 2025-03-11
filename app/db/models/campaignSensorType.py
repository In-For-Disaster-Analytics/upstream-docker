from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
)

from app.db.base import Base


class CampaignSensorType(Base):
    """
    Represents a type of a sensor in each campaign.
    """

    __tablename__ = "campaign_sensor_types"
    campaign_id = Column(
        Integer, ForeignKey("campaigns.campaignid"), nullable=False
    )
    sensor_type = Column(String(50), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint(
            "campaign_id", "sensor_type", name="campaign_sensor_types_pk"
        ),
        Index("idx_campaign_sensor_types", "sensor_type"),
    )
