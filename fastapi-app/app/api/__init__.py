from fastapi import APIRouter

from app.api.v1 import router as v1_router

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(v1_router)



