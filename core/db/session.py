import uuid
from contextvars import ContextVar, Token
from datetime import datetime, UTC
from typing import Union
from sqlalchemy import Update, Delete, Insert, String, Integer, UUID, DateTime
from sqlalchemy.orm import (
    Session,
    sessionmaker,
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

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


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

session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
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
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    try:
        yield session
    finally:
        await session.close()
