"""bounding box

Revision ID: 8f75d772b28a
Revises: ba26c4371225
Create Date: 2025-02-22 23:23:31.721196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f75d772b28a'
down_revision: Union[str, None] = 'ba26c4371225'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add coordinate columns for the bounding box to campaigns table
    op.add_column('campaigns', sa.Column('bbox_west', sa.Numeric))
    op.add_column('campaigns', sa.Column('bbox_east', sa.Numeric))
    op.add_column('campaigns', sa.Column('bbox_south', sa.Numeric))
    op.add_column('campaigns', sa.Column('bbox_north', sa.Numeric))

    # Create multicolumn indexes for the bounding box fields
    op.create_index(
        'idx_campaign_bbox_west_east',
        'campaigns',
        ['bbox_west', 'bbox_east']
    )

    op.create_index(
        'idx_campaign_bbox_north_south',
        'campaigns',
        ['bbox_north', 'bbox_south']
    )

    # Create multicolumn indexes for the date fields
    op.create_index(
        'idx_campaign_dates',
        'campaigns',
        ['startdate', 'enddate']
    )

    # Create a junction campaign_sensor_types table for sensor type association
    op.create_table(
        'campaign_sensor_types',
        sa.Column('campaign_id', sa.Integer),
        sa.Column('sensor_type', sa.String(50)),
        sa.ForeignKeyConstraint(('campaign_id', ), ['campaigns.campaignid']),
        sa.PrimaryKeyConstraint('campaign_id', 'sensor_type', name='campaign_sensor_types_pk')
    )

    # Create an index for the sensor_type field in the campaign_sensor_types table
    op.create_index(
        'idx_campaign_sensor_types',
        'campaign_sensor_types',
        ['sensor_type']
    )
    


def downgrade() -> None:
    op.drop_column('campaigns', 'bbox_west')
    op.drop_column('campaigns', 'bbox_east')
    op.drop_column('campaigns', 'bbox_south')
    op.drop_column('campaigns', 'bbox_north')

    #op.drop_index('idx_campaign_bbox_west_east', table_name='campaigns')
    #op.drop_index('idx_campaign_bbox_north_south', table_name='campaigns')

    #op.drop_index('idx_campaign_dates', table_name='campaigns')

    op.drop_table('campaign_sensor_types')
    #op.drop_index('idx_campaign_sensor_types',table_name='campaign_sensor_types')
