"""add upload_file_event table

Revision ID: 81b6b19bad45
Revises: 9e7f71ac2376
Create Date: 2025-03-31 14:16:50.017497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '81b6b19bad45'
down_revision: Union[str, None] = '9e7f71ac2376'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'upload_file_events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('time', sa.DateTime, server_default=func.now())
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('upload_file_events')
