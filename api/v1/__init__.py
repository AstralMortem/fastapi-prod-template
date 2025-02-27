from fastapi import APIRouter
from .auth import AuthController

router = APIRouter(prefix="/v1")
router.include_router(AuthController.as_router())
