def format_campaign(campaign):
    """
    Format campaign data for API v1 responses.

    Args:
        campaign: Campaign database model instance

    Returns:
        dict: Formatted campaign data according to v1 specifications
    """
    return {
        "id": campaign.campaignid,
        "name": campaign.campaignname,
        "description": campaign.description,
        "temporal_coverage": {
            "start_date": campaign.startdate.isoformat(),
            "end_date": campaign.enddate.isoformat() if campaign.enddate else None
        },
        "spatial_coverage": {
            "bbox": [
                campaign.bbox_west,
                campaign.bbox_south,
                campaign.bbox_east,
                campaign.bbox_north
            ],
            "center": [
                (campaign.bbox_west + campaign.bbox_east) / 2,
                (campaign.bbox_south + campaign.bbox_north) / 2
            ]
        },
        "sensor_types": [st.sensor_type for st in campaign.sensor_types],
        "stations_count": len(campaign.station)
    }