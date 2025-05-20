"""add_sensor_statistics_table

Revision ID: cab36a8ae270
Revises: 23762c788dd6
Create Date: 2025-05-19 19:14:24.372050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cab36a8ae270'
down_revision: Union[str, None] = '23762c788dd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create sensor_statistics table
    op.create_table(
        'sensor_statistics',
        sa.Column('sensorid', sa.Integer(), nullable=False),
        sa.Column('max_value', sa.Numeric(), nullable=True),
        sa.Column('min_value', sa.Numeric(), nullable=True),
        sa.Column('avg_value', sa.Numeric(), nullable=True),
        sa.Column('stddev_value', sa.Numeric(), nullable=True),
        sa.Column('percentile_90', sa.Numeric(), nullable=True),
        sa.Column('percentile_95', sa.Numeric(), nullable=True),
        sa.Column('percentile_99', sa.Numeric(), nullable=True),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('first_measurement_value', sa.Numeric(), nullable=True),
        sa.Column('first_measurement_collectiontime', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_measurement_value', sa.Numeric(), nullable=True),
        sa.Column('last_measurement_collectiontime', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('stats_last_updated', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('sensorid'),
        sa.ForeignKeyConstraint(['sensorid'], ['sensors.sensorid'], ondelete='CASCADE')
    )

    # Create index for the foreign key
    op.create_index('idx_sensor_statistics_sensorid', 'sensor_statistics', ['sensorid'])

    # Create index on measurements table for faster statistics calculation
    op.create_index('idx_measurements_sensorid_collectiontime', 'measurements', ['sensorid', 'collectiontime'])

    # Populate the statistics table with initial data
    # Note: We use execute() to run raw SQL since this is complex for SQLAlchemy operations
    op.execute("""
    INSERT INTO sensor_statistics (
        sensorid,
        max_value,
        min_value,
        avg_value,
        stddev_value,
        percentile_90,
        percentile_95,
        percentile_99,
        count,
        first_measurement_value,
        first_measurement_collectiontime,
        last_measurement_value,
        last_measurement_collectiontime,
        stats_last_updated
    )
    SELECT
        stats.sensorid,
        stats.max_val,
        stats.min_val,
        stats.avg_val,
        stats.stddev_val,
        stats.p90,
        stats.p95,
        stats.p99,
        stats.cnt,
        first.first_value,
        first.first_collectiontime,
        latest.last_value,
        latest.last_collectiontime,
        NOW()
    FROM (
        -- Basic statistics
        SELECT
            sensorid,
            MAX(measurementvalue) AS max_val,
            MIN(measurementvalue) AS min_val,
            AVG(measurementvalue) AS avg_val,
            STDDEV(measurementvalue) AS stddev_val,
            PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY measurementvalue) AS p90,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY measurementvalue) AS p95,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY measurementvalue) AS p99,
            COUNT(*) AS cnt
        FROM measurements
        GROUP BY sensorid
    ) stats
    JOIN (
        -- Latest values
        SELECT
            sensorid,
            measurementvalue AS last_value,
            collectiontime AS last_collectiontime
        FROM (
            SELECT
                sensorid,
                measurementvalue,
                collectiontime,
                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY collectiontime DESC) AS rn
            FROM measurements
        ) m
        WHERE rn = 1
    ) latest ON stats.sensorid = latest.sensorid
    JOIN (
        -- First values
        SELECT
            sensorid,
            measurementvalue AS first_value,
            collectiontime AS first_collectiontime
        FROM (
            SELECT
                sensorid,
                measurementvalue,
                collectiontime,
                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY collectiontime ASC) AS rn
            FROM measurements
        ) m
        WHERE rn = 1
    ) first ON stats.sensorid = first.sensorid
    """)



def downgrade():
    # Drop the index on measurements
    op.drop_index('idx_measurements_sensorid_collectiontime', table_name='measurements')

    # Drop the index on sensor_statistics
    op.drop_index('idx_sensor_statistics_sensorid', table_name='sensor_statistics')

    # Drop the table
    op.drop_table('sensor_statistics')

