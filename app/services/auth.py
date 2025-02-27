from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_session
from core.service import BaseService
from app.repositories.auth import AuthRepository
from core.utils.password import PasswordHelper, PasswordHelperProtocol
from app.models.auth import User, RefreshToken
import uuid
from fastapi.security import OAuth2PasswordRequestForm
from core.types import TokenType
from core.utils.jwt_helper import decode_token, DecodeError
from core.security.tokens import (
    generate_tokens_response,
    generate_token_logout_response,
)


class AuthService(BaseService[AuthRepository, User, uuid.UUID]):
    def __init__(
        self,
        repository: AuthRepository,
        password_helper: PasswordHelperProtocol = PasswordHelper(),
    ):
        super().__init__(repository)
        self.password_helper = password_helper

    async def get_user_by_login_fields(self, username: str):
        for field in settings.USER_LOGIN_FIELDS:
            instance = await self.repository.get_by_field(field, username)
            if instance is None:
                continue
            else:
                return instance
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    async def login(self, credentials: OAuth2PasswordRequestForm):
        instance = await self.get_user_by_login_fields(credentials.username)
        valid, new_hash = self.password_helper.verify_and_update(
            credentials.password, instance.hashed_password
        )
        if not valid:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        if new_hash:
            await self.repository.update(instance, {"hashed_password": new_hash})

        return generate_tokens_response(instance)

    async def logout(self, user: User):
        if user.refresh_token is not None:
            refresh_token_model = RefreshToken(**user.refresh_token)
            await self.repository.session.delete(refresh_token_model)
        return generate_token_logout_response()

    async def authorize(self, token: str, token_type: TokenType = "access"):
        error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
        try:
            decoded = decode_token(token, settings.JWT_AUTH_AUDIENCE)
        except DecodeError:
            raise error

        try:
            user_id = uuid.UUID(decoded.get("sub"))
        except Exception:
            raise error

        try:
            type_ = decoded.get("type")
            assert type_ == token_type, Exception("Invalid token type")
        except Exception:
            raise error

        return await self.get_by_id(user_id)


async def get_auth_service(session: AsyncSession = Depends(get_session)):
    return AuthService(AuthRepository(session))
