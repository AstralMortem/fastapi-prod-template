import uuid

from fastapi import Depends

from app.schemas import WriteSchema, UpdateSchema
from core.controller.sets import ReadControllerSet, CRUDController
from app.services.auth import AuthService, get_auth_service
from core.repository.base import ID
from core.schema import ReadSchema


class Read(ReadSchema):
    id: uuid.UUID


class Write(WriteSchema):
    password: str


class Update(UpdateSchema):
    password: str | None = None


class AuthController(CRUDController[AuthService, uuid.UUID, Read, Write, Update]):
    router_prefix = "/auth"

    service: AuthService = Depends(get_auth_service)
