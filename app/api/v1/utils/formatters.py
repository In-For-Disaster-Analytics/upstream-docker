from app.api.v1.schemas.campaign import ListCampaignsResponseItem, SummaryListCampaigns
from app.db.models.campaign import Campaign


def format_campaign(campaign: Campaign) -> ListCampaignsResponseItem:
    """
    Format campaign data for API v1 responses.

    Args:
        campaign: Campaign database model instance

    Returns:
        dict: Formatted campaign data according to v1 specifications
    """

    return ListCampaignsResponseItem(
        id=campaign.campaignid,
        name=campaign.campaignname,
        description=campaign.description,
        start_date=campaign.startdate,
        end_date=campaign.enddate,
        contact_name=campaign.contactname,
        contact_email=campaign.contactemail,
        allocation=campaign.allocation,
        summary=SummaryListCampaigns(
            sensor_types=None,
            variable_names=None,
        )
    )
