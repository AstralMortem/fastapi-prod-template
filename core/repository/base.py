import uuid
from functools import reduce
from typing import TypeVar, Generic
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.pagination import paginate, Params, Page
from core.utils.filters import BaseFilterModel
from core.db import Model

MODEL = TypeVar("MODEL", bound=Model)
ID = TypeVar("ID", bound=str | int | uuid.UUID)


class BaseRepository(Generic[MODEL, ID]):
    model: type[MODEL]

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

    async def list_all(
        self,
        pagination: Params,
        filter_model: BaseFilterModel | None = None,
        joins: set[str] | None = None,
    ) -> Page[MODEL]:
        query = select(self.model)
        return await self._filter_and_paginate(query, pagination, filter_model, joins)

    async def delete(self, model: MODEL) -> MODEL:
        await self.session.delete(model)
        return model

    async def _all(self, query: Select[MODEL]):
        query = await self.session.scalars(query)
        return query.all()

    async def _all_unique(self, query: Select[MODEL]):
        result = await self.session.execute(query)
        return result.unique.scalars().all()

    async def _filter_and_paginate(
        self,
        query: Select,
        pagination: Params,
        filter_model: BaseFilterModel | None = None,
        joins: set[str] | None = None,
    ):
        if joins is not None:
            query = self._join(query, joins)
        if filter_model is not None:
            query = filter_model.filter(query)
        return await paginate(self.session, query, pagination)

    def _join(self, query: Select, joins: set[str] | None):
        if joins is None:
            return query

        if not isinstance(joins, set):
            raise ValueError("Joins must be a set")

        return reduce(self._add_join_to_query, joins, query)

    def _add_join_to_query(self, query: Select, joins: set[str]):
        return getattr(self, "_join_" + joins)(query)
