"""add_station_location_fields

Revision ID: ed4fbf32ff56
Revises: 987aaf2c48d2
Create Date: 2025-03-20 16:14:56.149913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed4fbf32ff56'
down_revision: Union[str, None] = '987aaf2c48d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add station type
    op.add_column('stations', sa.Column('station_type', sa.String(), nullable=False))

    # Add static station location fields
    op.add_column('stations', sa.Column('static_latitude', sa.Float(), nullable=True))
    op.add_column('stations', sa.Column('static_longitude', sa.Float(), nullable=True))

    # Add mobile station bounding box fields
    op.add_column('stations', sa.Column('mobile_bbox_west', sa.Float(), nullable=True))
    op.add_column('stations', sa.Column('mobile_bbox_east', sa.Float(), nullable=True))
    op.add_column('stations', sa.Column('mobile_bbox_south', sa.Float(), nullable=True))
    op.add_column('stations', sa.Column('mobile_bbox_north', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove all new columns
    op.drop_column('stations', 'mobile_bbox_north')
    op.drop_column('stations', 'mobile_bbox_south')
    op.drop_column('stations', 'mobile_bbox_east')
    op.drop_column('stations', 'mobile_bbox_west')
    op.drop_column('stations', 'static_longitude')
    op.drop_column('stations', 'static_latitude')
    op.drop_column('stations', 'station_type')
