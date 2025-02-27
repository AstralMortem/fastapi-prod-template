from typing import TypeVar, Generic
from fastapi import HTTPException, status
from app.schemas import UpdateSchema
from core.repository.base import BaseRepository, MODEL, ID
from core.schema import WriteSchema
from core.utils.filters import BaseFilterModel
from core.utils.pagination import Params, Page

REPO = TypeVar("REPO", bound=BaseRepository)


class BaseService(Generic[REPO, MODEL, ID]):
    id = ID

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

    async def create(self, data: WriteSchema) -> MODEL:
        data = data.model_dump(exclude_unset=True)
        return await self.repository.create(data)

    async def patch(self, pk: ID, data: UpdateSchema) -> MODEL:
        instance = await self.get_by_id(pk)
        data_dict = data.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude_none=True
        )
        return await self.repository.update(instance, data_dict)

    async def update(self, pk: ID, data: UpdateSchema) -> MODEL:
        instance = await self.get_by_id(pk)
        data_dict = data.model_dump(exclude_unset=True, exclude_defaults=True)
        return await self.repository.update(instance, data_dict)

    async def delete(self, pk: ID) -> MODEL:
        instance = await self.get_by_id(pk)
        return await self.repository.delete(instance)

    def _not_found_error(self, text: str | None = None):
        if text:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=text)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item from {self.__class__.__name__} service not found",
        )
