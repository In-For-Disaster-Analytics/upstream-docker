from datetime import datetime
from pydantic import BaseModel, Field

# Pydantic model for incoming location data
class LocationsIn(BaseModel):
    stationid: int
    collectiontime: datetime
    geometry : str

class BoundingBoxFilter(BaseModel):
    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)
