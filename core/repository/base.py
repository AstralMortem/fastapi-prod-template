from functools import reduce
from typing import TypeVar, Generic
from sqlalchemy import select, Select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.pagination import AbstractPage, AbstractParams, paginate, Params, Page
from core.utils.filters import BaseFilterModel
from core.db import Model

MODEL = TypeVar('MODEL', bound=Model)
ID = TypeVar('ID')

class BaseRepository(Generic[MODEL, ID]):
    model: type[MODEL]
    pk_field: ID

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pk: ID) -> MODEL | None:
        return await self.session.get(self.model, pk)

    async def get_by_field(self, field: str, value: any) -> MODEL | None:
        qs = select(self.model).filter_by(**{field: value})
        return await self.session.scalar(qs)

    async def create(self, data: dict[str, any] = None) -> MODEL:
        if data is None:
            data = {}
        model = self.model(**data)
        self.session.add(model)
        await self.session.commit()
        return model

    async def update(self, model: Model, data: dict[str, any] = None) -> MODEL:
        for key, value in data.items() or {}:
            setattr(model, key, value)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def list_all(self, pagination: Params , filter_model: BaseFilterModel | None = None, joins_: set[str] | None = None) -> Page[MODEL]:
        query = select(self.model)
        if joins_ is not None:
            query = self._join(query, joins_)
        if filter_model is not None:
            query = filter_model.filter(query)

        return await paginate(self.session, query, pagination)


    async def delete(self, model: MODEL) -> MODEL:
        await self.session.delete(model)
        return model

    async def _all(self, query: Select[MODEL]):
        query = await self.session.scalars(query)
        return query.all()

    async def _all_unique(self, query: Select[MODEL]):
        result = await self.session.execute(query)
        return result.unique.scalars().all()

    def _join(self, query: Select, joins: set[str] | None):
        if joins is None:
            return query

        if not isinstance(joins, set):
            raise ValueError('Joins must be a set')

        return reduce(self._add_join_to_query, joins, query)


    def _add_join_to_query(self, query: Select, joins: set[str]):
        return getattr(self, "_join_" + joins)(query)