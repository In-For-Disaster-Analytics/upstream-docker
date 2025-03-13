"""delete_campaign_sensor_type_table

Revision ID: 8c70b3cdb856
Revises: 15da413ffe54
Create Date: 2025-03-13 09:31:06.310087

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c70b3cdb856"
down_revision: Union[str, None] = "15da413ffe54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("campaign_sensor_types")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "campaign_sensor_types",
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("sensor_type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.campaignid"],
        ),
        sa.PrimaryKeyConstraint(
            "campaign_id", "sensor_type", name="campaign_sensor_types_pk"
        ),
    )
    op.create_index(
        "idx_campaign_sensor_types",
        "campaign_sensor_types",
        ["sensor_type"],
        unique=False,
    )
