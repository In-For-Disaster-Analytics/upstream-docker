"""add_station_location_fields

Revision ID: ed4fbf32ff56
Revises: 987aaf2c48d2
Create Date: 2025-03-20 16:14:56.149913

"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed4fbf32ff56'
down_revision: Union[str, None] = '987aaf2c48d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add station type
    op.add_column('stations', sa.Column('station_type', sa.String(), nullable=True))
    op.execute("UPDATE stations SET station_type = 'static'")
    op.alter_column('stations', 'station_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.add_column('stations', sa.Column(
        "geometry",
        geoalchemy2.types.Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            from_text="ST_GeomFromEWKT",
            name="geometry",
        ),
        nullable=True,
    ))


def downgrade() -> None:
    # Remove all new columns
    op.drop_column('stations', 'geometry')
    op.drop_column('stations', 'station_type')
