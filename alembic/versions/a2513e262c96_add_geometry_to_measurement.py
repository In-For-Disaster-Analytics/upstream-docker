"""add geometry to measurement

Revision ID: a2513e262c96
Revises: 13373854a37f
Create Date: 2025-03-13 10:36:41.948085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'a2513e262c96'
down_revision: Union[str, None] = '13373854a37f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "measurements",
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("measurements", "geometry")
