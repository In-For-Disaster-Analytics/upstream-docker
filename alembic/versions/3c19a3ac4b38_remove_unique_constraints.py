"""remove unique constraints

Revision ID: 3c19a3ac4b38
Revises: 15da413ffe54
Create Date: 2024-03-25 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c19a3ac4b38"
down_revision: Union[str, None] = "15da413ffe54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove unique constraints
    op.drop_constraint("campaigns_campaignname_key", "campaigns", type_="unique")
    op.drop_constraint("stations_stationname_key", "stations", type_="unique")


def downgrade() -> None:
    """Downgrade schema."""
    # Restore unique constraints
    op.create_unique_constraint("campaigns_campaignname_key", "campaigns", ["campaignname"])
    op.create_unique_constraint("stations_stationname_key", "stations", ["stationname"])
