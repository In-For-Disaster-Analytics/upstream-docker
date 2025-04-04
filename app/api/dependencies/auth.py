import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.schemas.user import User
from app.pytas.http import TASClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")
ENVIRONMENT = os.getenv("ENVIRONMENT")


def authenticate_user(username, password):
    if ENVIRONMENT == "dev":
        return {"status": "success", "message": None, "result": True}
    else:
        client = TASClient(
            baseURL=os.getenv("tasURL"),
            credentials={
                "username": os.getenv("tasUser"),
                "password": os.getenv("tasSecret"),
            },
        )
        return client.authenticate(username, password)


# Async function to get the current user based on the provided OAuth2 token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    if ENVIRONMENT == "dev":
        return User(
            username="test",
        )

    try:
        user_dict = unhash(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(
        username=user_dict["username"],
    )


# Function to decode a JWT token using the specified secret and algorithm
def unhash(token):
    return jwt.decode(token, os.getenv("jwtSecret"), algorithms=[os.getenv("alg")])


def hash(payload):
    return jwt.encode(payload, os.getenv("jwtSecret"), algorithm=os.getenv("alg"))
