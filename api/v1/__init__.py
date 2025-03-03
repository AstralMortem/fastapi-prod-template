from fastapi import APIRouter
from .auth import AuthController, RoleController
from .user import UserController

router = APIRouter(prefix="/v1")
router.include_router(AuthController.as_router())
router.include_router(UserController.as_router())
router.include_router(RoleController.as_router())
