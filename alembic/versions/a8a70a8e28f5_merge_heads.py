"""merge heads

Revision ID: a8a70a8e28f5
Revises: 3c19a3ac4b38, 591d5138794b
Create Date: 2024-03-25 13:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a8a70a8e28f5"
down_revision: Union[str, Sequence[str], None] = ("3c19a3ac4b38", "591d5138794b")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
