from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.api.dependencies.auth import authenticate_user
from app.api.dependencies.pytas import get_allocations
from app.api.v1.main import api_router
load_dotenv()

app = FastAPI(title="Upstream Sensor Storage",
    description="Sensor Storage for Upstream data",
    version="0.0.1",
    contact={
        "name": "Will Mobley",
        "email": "wmobley@tacc.utexas.edu",
    }, )

app.include_router(api_router, prefix="/api/v1")

