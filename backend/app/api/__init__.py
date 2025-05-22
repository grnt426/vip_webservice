from fastapi import APIRouter
from .guilds import router as guilds_router
from .items import router as items_router
from .health import router as health_router

router = APIRouter(prefix="/api")
router.include_router(guilds_router, tags=["guilds"])
router.include_router(items_router, tags=["items"])
router.include_router(health_router, tags=["health"])