from fastapi import APIRouter

from app.api.v1.routes.campaigns.campaings import router as campaigns_router
from app.api.v1.routes.campaigns.campaing_stations import router as stations_router
from app.api.v1.routes.campaigns.campaign_station_sensors import router as campaign_station_sensors_router
from app.api.v1.routes.measurements import router as measurements_router
from app.api.v1.routes.upload_file.upload import router as upload_file_router

api_router = APIRouter()
api_router.include_router(campaigns_router)
api_router.include_router(stations_router)
api_router.include_router(campaign_station_sensors_router)
api_router.include_router(measurements_router)
api_router.include_router(upload_file_router)
