"""add modify update station function

Revision ID: 9e7f71ac2376
Revises: 2008f200556c
Create Date: 2025-03-27 10:41:11.167804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e7f71ac2376'
down_revision: Union[str, None] = '2008f200556c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #remove old function: update_station_bounding_box
    op.execute("""
        DROP FUNCTION IF EXISTS update_station_bounding_box(INTEGER);
    """)
    op.execute("""
    CREATE OR REPLACE FUNCTION update_station_geometry(station_id_param INTEGER)
    RETURNS VOID AS $$
    BEGIN
        -- Update the bounding_box for the specified station
        -- by calculating the envelope of all associated measurement points
        UPDATE stations
        SET geometry = subquery.bbox
        FROM (
            SELECT
                ST_Envelope(ST_Collect(geometry)) AS bbox
            FROM
                sensors
            LEFT JOIN measurements ON sensors.sensorid = measurements.sensorid
            WHERE
                sensors.stationid = station_id_param
            GROUP BY
                sensors.stationid
        ) AS subquery
        WHERE stations.stationid = station_id_param;

        -- If no measurements exist for this station, set bounding_box to NULL
        IF NOT FOUND THEN
            UPDATE stations
            SET geometry = NULL
            WHERE stationid = station_id_param;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        SELECT update_station_geometry(stationid) FROM stations;
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
