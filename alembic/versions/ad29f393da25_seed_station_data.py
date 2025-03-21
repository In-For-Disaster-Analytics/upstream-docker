"""seed_station_data

Revision ID: ad29f393da25
Revises: f06c5b3c4458
Create Date: 2025-03-19 16:24:39.556710

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'ad29f393da25'
down_revision: Union[str, None] = 'f06c5b3c4458'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    return
    """Add seed data for stations."""
    stations_table = sa.table('stations',
        sa.column('stationid', sa.Integer),
        sa.column('campaignid', sa.Integer),
        sa.column('stationname', sa.String),
        sa.column('projectid', sa.String),
        sa.column('description', sa.String),
        sa.column('contactname', sa.String),
        sa.column('contactemail', sa.String),
        sa.column('active', sa.Boolean),
        sa.column('startdate', sa.DateTime)
    )

    # Adding stations for the Weather Station Network campaign (campaign_id: 2)
    op.bulk_insert(stations_table, [
        {
            'stationid': 1,
            'campaignid': 2,
            'stationname': 'Austin Downtown',
            'projectid': 'ATX-001',
            'description': 'Central Austin weather monitoring station located in downtown area',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'active': True,
            'startdate': datetime(2024, 3, 1)
        },
        {
            'stationid': 2,
            'campaignid': 2,
            'stationname': 'Houston Medical Center',
            'projectid': 'HOU-001',
            'description': 'Weather station in Texas Medical Center area monitoring urban climate',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'active': True,
            'startdate': datetime(2024, 3, 1)
        },
        {
            'stationid': 3,
            'campaignid': 2,
            'stationname': 'Dallas North',
            'projectid': 'DFW-001',
            'description': 'North Dallas station monitoring suburban weather patterns',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'active': True,
            'startdate': datetime(2024, 3, 1)
        },
        {
            'stationid': 4,
            'campaignid': 2,
            'stationname': 'San Antonio River Walk',
            'projectid': 'SAT-001',
            'description': 'Downtown San Antonio station near River Walk monitoring urban microclimate',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'active': True,
            'startdate': datetime(2024, 3, 1)
        },
        {
            'stationid': 5,
            'campaignid': 2,
            'stationname': 'El Paso Desert',
            'projectid': 'ELP-001',
            'description': 'Station monitoring arid climate conditions in West Texas',
            'contactname': 'Jane Smith',
            'contactemail': 'jane.smith@example.com',
            'active': True,
            'startdate': datetime(2024, 3, 1)
        },
        # Test station for Test Campaign 2024 (campaign_id: 1)
        {
            'stationid': 6,
            'campaignid': 1,
            'stationname': 'Test Station Alpha',
            'projectid': 'TEST-001',
            'description': 'Test station for development and testing purposes',
            'contactname': 'John Doe',
            'contactemail': 'john.doe@example.com',
            'active': True,
            'startdate': datetime(2024, 1, 1)
        }
    ])


def downgrade() -> None:
    """Remove seed data."""
    op.execute('DELETE FROM stations WHERE stationid IN (1, 2, 3, 4, 5, 6)')
