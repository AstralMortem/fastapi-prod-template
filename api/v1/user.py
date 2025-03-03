import uuid

from fastapi import Depends

from app.schemas.auth import UserReadSchema, UserUpdateSchema, UserCreateSchema
from app.services.auth import AuthService, get_auth_service
from core.controller import Controller, as_route
from core.security.permission import access_token_required, HasPermission, HasRole, Authorize, Actions
from core.security.mixins import SuperUser

class UserController(Controller):
    router_prefix = "/users"
    resource_name = "users"
    service: AuthService = Depends(get_auth_service)


    @as_route("/me", method="GET", response_model=UserReadSchema)
    async def get_me(self, user = Depends(access_token_required())):
        return user

    @as_route("/me", method="PATCH", response_model=UserReadSchema)
    async def update_me(self, data: UserUpdateSchema, user = Depends(access_token_required())):
        await self.service.update_instance(user, data)

    @as_route('/{id}', method="GET", response_model=UserReadSchema, dependencies=[Authorize(SuperUser | HasPermission(Actions.READ))])
    async def get_user(self, id: uuid.UUID):
        return await self.service.get_by_id(id)

    @as_route("/{id}", method="PATCH", response_model=UserUpdateSchema, dependencies=[Authorize(SuperUser | HasPermission(Actions.UPDATE))])
    async def update_user(self, id: uuid.UUID, data: UserUpdateSchema):
        return await self.service.update(id, data)

    @as_route("/{id}", method="DELETE", response_model=UserReadSchema, dependencies=[Authorize(SuperUser | HasPermission(Actions.DELETE))])
    async def delete_user(self, id: uuid.UUID):
        return await self.service.delete(id)

    @as_route("/", method="POST", response_model=UserReadSchema, dependencies=[Authorize(SuperUser | HasPermission(Actions.CREATE))])
    async def create_user(self, data: UserCreateSchema):
        return await self.service.signup(data, safe=False)