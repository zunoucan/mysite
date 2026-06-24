from fastapi import APIRouter
from .listings import router as listings_router
from .apply import router as apply_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(listings_router)
api_router.include_router(apply_router)
