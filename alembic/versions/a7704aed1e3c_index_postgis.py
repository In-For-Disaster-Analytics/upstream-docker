"""index_postgis

Revision ID: a7704aed1e3c
Revises: 8f75d772b28a
Create Date: 2025-02-23 03:12:56.202769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7704aed1e3c'
down_revision: Union[str, None] = '8f75d772b28a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    query_ = """
        CREATE INDEX idx_campaign_bbox_gist ON campaigns USING GIST (
            ST_MakeEnvelope(bbox_west, bbox_south, bbox_east, bbox_north, 4326)
        );
    """
    conn = op.get_bind()
    conn.execute(query_)


def downgrade() -> None:
    pass
