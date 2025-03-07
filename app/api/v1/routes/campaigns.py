from fastapi import APIRouter

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.get("/")
async def get_campaigns():
    return {"message": "Hello, World!"}

