"""seed_campaign_data

Revision ID: f06c5b3c4458
Revises: a2513e262c96
Create Date: 2025-03-19 16:24:39.556710

"""
import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'f06c5b3c4458'
down_revision: Union[str, None] = 'a2513e262c96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add seed data for campaigns."""
    campaigns_table = sa.table('campaigns',
        sa.column('campaignid', sa.Integer),
        sa.column('campaignname', sa.String),
        sa.column('description', sa.String),
        sa.column('contactname', sa.String),
        sa.column('contactemail', sa.String),
        sa.column('startdate', sa.DateTime),
        sa.column('enddate', sa.DateTime),
        sa.column('allocation', sa.String),
        sa.column('bbox_west', sa.Float),
        sa.column('bbox_east', sa.Float),
        sa.column('bbox_south', sa.Float),
        sa.column('bbox_north', sa.Float)
    )

    op.bulk_insert(campaigns_table, [
        {
            'campaignid': 1,
            'campaignname': 'Test Campaign 2024',
            'description': 'A test campaign for development purposes',
            'contactname': 'John Doe',
            'contactemail': 'john.doe@example.com',
            'startdate': datetime(2024, 1, 1),
            'enddate': datetime(2024, 12, 31),
            'allocation': 'TEST-123',
            'bbox_west': -98.0,
            'bbox_east': -96.0,
            'bbox_south': 30.0,
            'bbox_north': 31.0
        },
        {
            'campaignid': 2,
            'campaignname': 'Weather Station Network',
            'description': 'Network of weather stations across Texas',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'startdate': datetime(2024, 3, 1),
            'enddate': datetime(2025, 2, 28),
            'allocation': 'WEATHER-456',
            'bbox_west': -106.65,
            'bbox_east': -93.51,
            'bbox_south': 25.84,
            'bbox_north': 36.50
        }
    ])


def downgrade() -> None:
    """Remove seed data."""
    op.execute('DELETE FROM campaigns WHERE campaignid IN (1, 2)')

