from fastapi import APIRouter
from .guilds import router as guilds_router
from .items import router as items_router
from .health import router as health_router
from .endpoints.users import router as users_router
from .endpoints.accounts import router as accounts_router
from .endpoints.moderation import router as moderation_router

router = APIRouter(prefix="/api")
router.include_router(guilds_router, tags=["guilds"])
router.include_router(items_router, tags=["items"])
router.include_router(health_router, tags=["health"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(accounts_router, tags=["accounts"])
router.include_router(moderation_router, prefix="/moderation", tags=["moderation"])