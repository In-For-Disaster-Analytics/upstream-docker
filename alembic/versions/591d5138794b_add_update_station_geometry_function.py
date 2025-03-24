"""add update station geometry function

Revision ID: 591d5138794b
Revises: ed4fbf32ff56
Create Date: 2025-03-24 12:29:22.497928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '591d5138794b'
down_revision: Union[str, None] = 'ed4fbf32ff56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.execute("""
    CREATE OR REPLACE FUNCTION update_station_bounding_box(station_id_param INTEGER)
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
                measurements
            WHERE
                stationid = station_id_param
            GROUP BY
                stationid
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
        SELECT update_station_bounding_box(stationid) FROM stations;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP FUNCTION IF EXISTS update_station_bounding_box(INTEGER);
    """)
