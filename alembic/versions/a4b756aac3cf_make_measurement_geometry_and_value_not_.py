"""make measurement geometry and value not null

Revision ID: a4b756aac3cf
Revises: seed_mobile_co2_station
Create Date: 2025-04-01 11:52:21.054852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b756aac3cf'
down_revision: Union[str, None] = 'seed_mobile_co2_station'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('measurements', 'geometry', nullable=False)
    op.alter_column('measurements', 'measurementvalue', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('measurements', 'geometry', nullable=True)
    op.alter_column('measurements', 'measurementvalue', nullable=True)
