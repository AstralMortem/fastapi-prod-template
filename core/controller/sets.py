from fastapi import Depends

from core.utils.pagination import Params, Page
from .base import Controller, as_route
from typing import (
    Generic,
    TypeVar,
    TYPE_CHECKING,
    ClassVar,
    Annotated,
    get_args,
    Self,
    Union,
    Literal,
)
from core.service.base import BaseService, ID
from core.schema import ReadSchema, WriteSchema, UpdateSchema

SERVICE = TypeVar("SERVICE", bound=BaseService)
READ_SCHEMA = TypeVar("READ_SCHEMA", bound=ReadSchema)
WRITE_SCHEMA = TypeVar("WRITE_SCHEMA", bound=WriteSchema)
UPDATE_SCHEMA = TypeVar("UPDATE_SCHEMA", bound=UpdateSchema)


class ReadControllerSet(Generic[SERVICE, ID, READ_SCHEMA], Controller):
    service: SERVICE

    @as_route("/{id}", "GET", override_args=("id", ID), response_model=READ_SCHEMA)
    async def get(self, id):
        return await self.service.get_by_id(id)

    @as_route("/", method="GET", response_model=(Page, READ_SCHEMA))
    async def list(self, pagination: Params = Depends()):
        return await self.service.list(pagination)


class WriteControllerSet(
    Generic[SERVICE, ID, READ_SCHEMA, WRITE_SCHEMA, UPDATE_SCHEMA], Controller
):
    update_method: ClassVar[Literal["PUT", "PATCH", "*"]] = "PATCH"
    service: SERVICE

    @as_route(
        "/",
        method="POST",
        response_model=READ_SCHEMA,
        override_args=("data", WRITE_SCHEMA),
    )
    async def post(self, data):
        return await self.service.create(data)

    if update_method == "PATCH" or update_method == "*":

        @as_route(
            "/{id}",
            method="PATCH",
            override_args=[("id", ID), ("data", UPDATE_SCHEMA)],
            response_model=READ_SCHEMA,
        )
        async def patch(self, id, data):
            return await self.service.patch(id, data)

    if update_method == "PUT" or update_method == "*":

        @as_route(
            "/{id}",
            method="PUT",
            override_args=[("id", ID), ("data", UPDATE_SCHEMA)],
            response_model=READ_SCHEMA,
        )
        async def put(self, id, data):
            return await self.service.update(id, data)

    @as_route("/{id}", method="DELETE", override_args=("id", ID))
    async def delete(self, id):
        return await self.service.delete(id)


class CRUDControllerSet(
    Generic[SERVICE, ID, READ_SCHEMA, WRITE_SCHEMA, UPDATE_SCHEMA],
    ReadControllerSet[SERVICE, ID, READ_SCHEMA],
    WriteControllerSet[SERVICE, ID, READ_SCHEMA, WRITE_SCHEMA, UPDATE_SCHEMA],
):
    service: SERVICE
