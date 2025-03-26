"""add function update geometry

Revision ID: 2008f200556c
Revises: c47e335b363e
Create Date: 2025-03-26 12:17:05.793661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2008f200556c'
down_revision: Union[str, None] = 'c47e335b363e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE OR REPLACE FUNCTION update_campaign_geometry(campaign_id_param INTEGER)
    RETURNS VOID AS $$
    BEGIN
        -- Update the geometry for the specified campaign
        -- by calculating the envelope of all associated stations
        UPDATE campaigns
        SET geometry = subquery.bbox
        FROM (
            SELECT
                ST_Envelope(ST_Collect(s.geometry)) AS bbox
            FROM
                campaigns c
                JOIN stations s ON c.campaignid = s.campaignid
            WHERE
                c.campaignid = campaign_id_param
                AND s.geometry IS NOT NULL
            GROUP BY
                c.campaignid
        ) AS subquery
        WHERE campaigns.campaignid = campaign_id_param;

        -- If no stations with geometry exist for this campaign, set geometry to NULL
        IF NOT FOUND THEN
            UPDATE campaigns
            SET geometry = NULL
            WHERE campaignid = campaign_id_param;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        SELECT update_campaign_geometry(campaignid) FROM campaigns;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP FUNCTION IF EXISTS update_campaign_geometry(INTEGER);
    """)
