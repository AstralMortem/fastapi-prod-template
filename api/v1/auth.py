from app.models.auth import User
from app.schemas.auth import UserCreateSchema
from core.controller import as_route, Controller

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.security import (
    TokenResponse,
    access_token_required,
    AuthService,
    get_auth_service, Authorize,
)
from core.config import settings
from core.security.permission import HasRole, HasPermission


class AuthController(Controller):
    router_prefix = "/auth"
    resource_name = "auth"

    service: AuthService = Depends(get_auth_service)

    @as_route(
        "/login",
        method="POST",
        response_model=TokenResponse if settings.AUTH_METHOD == "header" else None,
    )
    async def password_login(self, credentials: OAuth2PasswordRequestForm = Depends()):
        return await self.service.login(credentials)

    @as_route("/logout", method="POST")
    async def logout(self, user: User = Depends(access_token_required())):
        return await self.service.logout(user)


    @as_route("/signup", method="POST")
    async def signup(self, data: UserCreateSchema):
        return await self.service.signup(data)