"""merge multiple heads

Revision ID: 23762c788dd6
Revises: 755f68973d16, 80811109be28
Create Date: 2025-04-07 11:03:56.065712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23762c788dd6'
down_revision: Union[str, None] = ('755f68973d16', '80811109be28')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
