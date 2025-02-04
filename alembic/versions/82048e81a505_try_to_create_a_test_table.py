"""try to create a test table

Revision ID: 82048e81a505
Revises: 
Create Date: 2025-02-04 20:35:22.410784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82048e81a505'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'vlad_alembic_test',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50))
    )


def downgrade() -> None:
    op.drop_table('vlad_alembic_test')
