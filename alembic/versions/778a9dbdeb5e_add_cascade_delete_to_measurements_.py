"""add cascade delete to measurements.sensorid foreign key

Revision ID: 778a9dbdeb5e
Revises: add_unique_constraint_to_values
Create Date: 2025-08-02 15:47:56.175249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '778a9dbdeb5e'
down_revision: Union[str, None] = 'add_unique_constraint_to_values'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing foreign key constraint
    op.drop_constraint('measurements_sensorid_fkey', 'measurements', type_='foreignkey')
    
    # Add the new foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'measurements_sensorid_fkey',
        'measurements',
        'sensors',
        ['sensorid'],
        ['sensorid'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the CASCADE foreign key constraint
    op.drop_constraint('measurements_sensorid_fkey', 'measurements', type_='foreignkey')
    
    # Recreate the original foreign key constraint without CASCADE
    op.create_foreign_key(
        'measurements_sensorid_fkey',
        'measurements',
        'sensors',
        ['sensorid'],
        ['sensorid']
    )
