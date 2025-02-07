"""adding variablename column to sensors table

Revision ID: ba26c4371225
Revises: 82048e81a505
Create Date: 2025-02-04 23:02:04.070916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba26c4371225'
down_revision: Union[str, None] = '82048e81a505'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sensors', sa.Column('variablename', sa.String()))


def downgrade() -> None:
    pass
