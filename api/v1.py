from fastapi import APIRouter
from core.controllers import BaseController

router = APIRouter()

router.include_router(BaseController.as_view())