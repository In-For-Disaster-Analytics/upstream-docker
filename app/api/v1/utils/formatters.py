from app.api.v1.schemas.campaign import CampaignsOut
from app.db.models.campaign import Campaign


def format_campaign(campaign: Campaign) -> CampaignsOut:
    """
    Format campaign data for API v1 responses.

    Args:
        campaign: Campaign database model instance

    Returns:
        dict: Formatted campaign data according to v1 specifications
    """

    if (
        campaign.bbox_west is None
        or campaign.bbox_east is None
        or campaign.bbox_south is None
        or campaign.bbox_north is None
    ):
        spatial_coverage = None
    else:
        spatial_coverage = {
            "bbox": [
                campaign.bbox_west,
                campaign.bbox_south,
                campaign.bbox_east,
                campaign.bbox_north,
            ],
            "center": [
                (campaign.bbox_west + campaign.bbox_east) / 2,
                (campaign.bbox_south + campaign.bbox_north) / 2,
            ],
        }
    print(spatial_coverage)
    return CampaignsOut(
        id=campaign.campaignid,
        name=campaign.campaignname,
        description=campaign.description,
        start_date=campaign.startdate,
        end_date=campaign.enddate,
        contact_name=campaign.contactname,
        contact_email=campaign.contactemail,
    )
