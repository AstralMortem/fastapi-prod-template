import uuid
from contextvars import ContextVar, Token
from typing import Union
from sqlalchemy import Update, Delete, Insert, String, Integer, UUID
from sqlalchemy.orm import (
    Session,
    mapped_column,
    Mapped,
    declared_attr,
    DeclarativeBase,
)
from core.config import settings
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from core.utils.string import pluralize, camel2snake


engines = {
    "writer": create_async_engine(settings.DATABASE_URL, pool_recycle=3600),
    "reader": create_async_engine(settings.DATABASE_URL, pool_recycle=3600),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        return engines["reader"].sync_engine


async_session_factory = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
    **settings.SQLALCHEMY_ENGINE_CONFIG,
)



class Model(DeclarativeBase):
    __without_default_pk__ = False

    @declared_attr.directive
    def __tablename__(cls):
        return pluralize(camel2snake(cls.__name__))

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if (
            settings.DEFAULT_PK_FIELD_NAME
            and not hasattr(cls, settings.DEFAULT_PK_FIELD_NAME)
            and not cls.__without_default_pk__
        ):
            if settings.DEFAULT_PK_FIELD_TYPE == str:
                column = mapped_column(String, primary_key=True)
            elif settings.DEFAULT_PK_FIELD_TYPE == int:
                column = mapped_column(Integer, primary_key=True, autoincrement=True)
            elif settings.DEFAULT_PK_FIELD_TYPE == uuid.UUID:
                column = mapped_column(
                    UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
                )
            else:
                raise ValueError(
                    f"Invalid DEFAULT_PK_FIELD_TYPE: {settings.DEFAULT_PK_FIELD_TYPE}"
                )

            setattr(cls, settings.DEFAULT_PK_FIELD_NAME, column)
            cls.__annotations__[settings.DEFAULT_PK_FIELD_NAME] = Mapped[
                settings.DEFAULT_PK_FIELD_TYPE
            ]

        super().__init_subclass__(**kwargs)


async def get_session():

    async with async_session_factory() as session:
        try:
            yield session
        except Exception as error:
            await session.rollback()
            raise error
        finally:
            await session.close()
