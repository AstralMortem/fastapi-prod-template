from app.models.auth import User
from app.schemas.auth import UserCreateSchema, UserReadSchema, RoleReadSchema, RoleCreateSchema, RoleUpdateSchema
from app.services.auth import RoleService, get_role_service, get_auth_service, AuthService
from core.controller import as_route, Controller, CRUDControllerSet

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.security.mixins import SuperUser
from core.security.permission import (
    access_token_required, Authorize, HasPermission, Actions
)
from core.security.tokens import TokenResponse

from core.config import settings



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

    @as_route("/signup", method="POST", response_model=UserReadSchema)
    async def signup(self, data: UserCreateSchema):
        return await self.service.signup(data)

class RoleController(CRUDControllerSet[RoleService, settings.DEFAULT_PK_FIELD_TYPE, RoleReadSchema, RoleCreateSchema, RoleUpdateSchema]):
    router_prefix = "/roles"
    resource_name = "role"
    service: RoleService = Depends(get_role_service)
    global_dependencies = [Authorize(SuperUser | HasPermission(Actions.ALL))]

    @as_route("/{codename}", method="GET", response_model=RoleReadSchema)
    async def get(self, codename:str):
        return await self.service.get_by_rolename(codename)
