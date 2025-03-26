"""add campaign geometry

Revision ID: c47e335b363e
Revises: a8a70a8e28f5
Create Date: 2025-03-26 12:11:24.426313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2 as ga

# revision identifiers, used by Alembic.
revision: str = 'c47e335b363e'
down_revision: Union[str, None] = 'a8a70a8e28f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('campaigns', sa.Column('geometry', ga.Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('campaigns', 'geometry')
