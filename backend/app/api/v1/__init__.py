from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.location import router as location_router
from app.api.v1.properties import router as properties_router
from app.api.v1.ai import router as ai_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(location_router, prefix="/location", tags=["location"])
api_router.include_router(properties_router, prefix="/properties", tags=["properties"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
