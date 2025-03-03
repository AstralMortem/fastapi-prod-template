from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserCreateSchema
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
    generate_token_logout_response, generate_access_token, generate_refresh_token,
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

        access_token = generate_access_token(instance)
        refresh_token = generate_refresh_token(instance)

        # TODO: store refresh token in db


        return generate_tokens_response(instance, access_token, refresh_token)

    async def logout(self, user: User):
        if user.refresh_token is not None:
            refresh_token_model = RefreshToken(**user.refresh_token)
            await self.repository.session.delete(refresh_token_model)
        return generate_token_logout_response()

    async def authorize(self, token: str, token_type: TokenType = "access", request: Request | None = None):
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

        instance = await self.get_by_id(user_id)
        await self.on_after_authorized(token, instance, request)

    async def signup(self, data: UserCreateSchema, request: Request | None = None):
        for field in settings.USER_LOGIN_FIELDS:
            user = await self.repository.get_by_field(field, getattr(data,field))
            if user is not None:
                raise HTTPException(status.HTTP_403_FORBIDDEN, f"User with same {'/'.join(settings.USER_LOGIN_FIELDS)} already exist")

        payload = data.model_dump()
        payload["hashed_password"] = self.password_helper.hash(payload.pop("password"))
        payload["is_active"] = settings.USER_IS_ACTIVE_DEFAULT
        created_user = await self.repository.create(payload)
        # Add default role to user
        created_user = await self._set_default_role(created_user)
        await self.on_after_signup(request, created_user, payload)
        return created_user

    async def _set_default_role(self, instance: User):
        if settings.USER_DEFAULT_ROLE_NAME:
            role = await self.repository.get_role_by_codename(settings.USER_DEFAULT_ROLE_NAME)
            if role is None:
                raise HTTPException(status.HTTP_403_FORBIDDEN, f"Role with name {settings.USER_DEFAULT_ROLE_NAME} not exists")
            instance.roles.append(role)
            await self.repository.session.commit()
            await self.repository.session.refresh(instance)
            return instance
        return instance


    async def on_after_signup(self,request: Request | None, instance: User, payload: dict[str, any]):
        """Called after user created in db"""

    async def on_after_authorized(self, token: str, instance: User, request:Request | None):
        """Called after user authorized"""



async def get_auth_service(session: AsyncSession = Depends(get_session)):
    return AuthService(AuthRepository(session))
