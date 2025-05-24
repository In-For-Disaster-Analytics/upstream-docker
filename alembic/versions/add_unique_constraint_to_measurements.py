"""add unique constraint to measurements

Revision ID: add_unique_constraint_to_measurements
Revises: 361b892599c6
Create Date: 2024-03-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_unique_constraint_to_values'
down_revision = '361b892599c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique constraint on sensorid, collectiontime, and geometry
    op.create_unique_constraint(
        'uq_measurements_sensor_time',
        'measurements',
        ['sensorid', 'collectiontime']
    )


def downgrade() -> None:
    # Remove the unique constraint
    op.drop_constraint(
        'uq_measurements_sensor_time',
        'measurements',
        type_='unique'
    )