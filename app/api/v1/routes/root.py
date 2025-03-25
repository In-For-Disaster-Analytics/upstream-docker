import jwt
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from app.api.dependencies.auth import authenticate_user

router = APIRouter()

load_dotenv()

JWT_SECRET = os.getenv("jwtSecret")

if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not set")

# Route for user authentication and token generation
@router.post("/token", tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    authenticated = authenticate_user(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Create jwt token
    return {
        "access_token": create_token(form_data.username),
        "token_type": "bearer",
    }


def create_token(username: str):
    return jwt.encode({"username": username}, JWT_SECRET, algorithm="HS256")
