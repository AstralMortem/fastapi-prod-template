from fastapi import APIRouter
from core.config import settings
from .v1 import router as v1_router

router = APIRouter(prefix=settings.GLOBAL_ROUTER_PREFIX)
router.include_router(v1_router)
