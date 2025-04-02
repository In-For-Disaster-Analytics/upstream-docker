"""add foreign key to upload_file_events for sensors and measurements

Revision ID: 755f68973d16
Revises: 81b6b19bad45
Create Date: 2025-03-31 16:19:11.146840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '755f68973d16'
down_revision: Union[str, None] = '81b6b19bad45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE measurements
            ADD COLUMN upload_file_events_id integer REFERENCES 
               upload_file_events (id) ON DELETE CASCADE;
    """)

    op.execute("""
        ALTER TABLE sensors
            ADD COLUMN upload_file_events_id integer REFERENCES 
               upload_file_events (id) ON DELETE CASCADE;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("measurements", "upload_file_events_id")
    op.drop_column("sensors", "upload_file_events_id")
