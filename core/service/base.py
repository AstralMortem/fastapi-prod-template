from typing import TypeVar, Generic
from fastapi import HTTPException, status, Request
from core.schema import UpdateSchema
from core.repository.base import BaseRepository, MODEL, ID
from core.schema import WriteSchema
from core.utils.filters import BaseFilterModel
from core.utils.pagination import Params, Page

REPO = TypeVar("REPO", bound=BaseRepository)


class BaseService(Generic[REPO, MODEL, ID]):
    def __init__(self, repo: REPO):
        self.repository = repo

    async def get_by_id(self, pk: ID) -> MODEL:
        instance = await self.repository.get_by_id(pk)
        if instance is None:
            raise self._not_found_error()
        return instance

    async def list(
        self, pagination: Params, filters: BaseFilterModel | None = None
    ) -> Page[MODEL]:
        return await self.repository.list_all(pagination, filters)

    async def create(self, data: WriteSchema, request: Request | None = None) -> MODEL:
        data_dict = data.model_dump(exclude_unset=True)
        await self.on_before_create(request, data_dict)
        instance = await self.repository.create(data_dict)
        await self.on_after_create(request, data_dict, instance)
        return instance

    async def patch(self, pk: ID, data: UpdateSchema, request: Request | None = None) -> MODEL:
        instance = await self.get_by_id(pk)
        data_dict = data.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude_none=True
        )
        return await self._update(instance, data_dict, request)

    async def update(self, pk: ID, data: UpdateSchema, request: Request | None = None) -> MODEL:
        instance = await self.get_by_id(pk)
        data_dict = data.model_dump(exclude_unset=True, exclude_defaults=True)
        return await self._update(instance, data_dict, request)

    async def _update(self, instance: MODEL, data: dict[str, any], request: Request | None = None):
        await self.on_before_update(request, data, instance)
        updated = await self.repository.update(instance, data)
        await self.on_after_update(request,data, updated)
        return updated

    async def delete(self, pk: ID, request: Request | None = None) -> MODEL:
        instance = await self.get_by_id(pk)
        await self.on_before_delete(request, instance)
        await self.repository.delete(instance)
        await self.on_after_delete(request, instance)
        return instance

    def _not_found_error(self, text: str | None = None):
        if text:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=text)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item from {self.__class__.__name__} service not found",
        )


    # Default events
    async def on_before_delete(self, request: Request | None, item: MODEL):
        """Called before item deleted from db"""

    async def on_after_delete(self, request: Request | None, item: MODEL):
        """Called after item was deleted from db"""

    async def on_before_update(self,request: Request | None, data: dict[str, any], old_instance: MODEL ):
        """Called on before item was updated"""

    async def on_after_update(self, request: Request | None, data: dict[str, any], new_instance: MODEL):
        """Called after item was updated"""

    async def on_before_create(self, request: Request | None, data: dict[str, any]):
        """Called before item created"""

    async def on_after_create(self, request: Request | None, data: dict[str, any], new_instance: MODEL):
        """Called after item created in db"""