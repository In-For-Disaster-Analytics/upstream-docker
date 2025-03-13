"""delete_location_table

Revision ID: 13373854a37f
Revises: 8c70b3cdb856
Create Date: 2025-03-13 10:15:32.220264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13373854a37f'
down_revision: Union[str, None] = '8c70b3cdb856'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('measurements', 'locationid')
    op.drop_table('locations')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('locations',
        sa.Column('locationid', sa.Integer, primary_key=True),
        sa.Column('stationid', sa.Integer, nullable=True),
        sa.Column('collectiontime', sa.DateTime, nullable=True),
        sa.Column('geometry', sa.Geometry('POINT', srid=4326), nullable=True),
    )
