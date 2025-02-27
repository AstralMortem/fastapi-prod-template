from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from core.service import BaseService
from app.repositories.auth import AuthRepository
from app.models.auth import User
import uuid


class AuthService(BaseService[AuthRepository, User, uuid.UUID]):
    id = uuid.UUID


async def get_auth_service(session: AsyncSession = Depends(get_session)):
    return AuthService(AuthRepository(session))
