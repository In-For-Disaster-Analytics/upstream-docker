from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.api.dependencies.auth import authenticate_user
from app.api.dependencies.pytas import get_allocations
from app.api.v1.main import api_router

app = FastAPI(title="Upstream Sensor Storage",
    description="Sensor Storage for Upstream data",
    version="0.0.1",
    contact={
        "name": "Will Mobley",
        "email": "wmobley@tacc.utexas.edu",
    }, )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.include_router(api_router, prefix="/api/v1")


# Route for user authentication and token generation
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    authenticated = authenticate_user(form_data.username, form_data.password)

    if not authenticated:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(    get_allocations(form_data.username))
    user_dict = {'username':form_data.username, 'password':form_data.password}

    return {"access_token": hash(user_dict), "token_type": "bearer"}

