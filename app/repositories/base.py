from typing import TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Model
from abc import ABC

MODEL = TypeVar('MODEL', bound=Model)
ID = TypeVar('ID')


class BaseRepository(Generic[MODEL, ID]):
    model: type[MODEL]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pk: ID) -> MODEL | None:
        return await self.session.get(self.model, pk)

    async def get_by_field(self, field: str, value: any) -> MODEL | None:
        qs = select(self.model).filter_by(**{field: value})
        return await self.session.scalar(qs)