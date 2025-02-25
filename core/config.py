import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, MariaDBDsn, MySQLDsn, Field
from fastapi_pagination.types import ParamsType



class Settings(BaseSettings):
    DEBUG: bool = True

    DATABASE_URL: PostgresDsn | MariaDBDsn | MySQLDsn | str = "sqlite+aiosqlite:///test.db"
    SQLALCHEMY_ENGINE_CONFIG: dict[str, Any] = {}
    DEFAULT_PK_FIELD_NAME: str | None = "id"
    DEFAULT_PK_FIELD_TYPE: type[str] | type[int] | type[uuid.UUID] | type[datetime] = int
    PAGINATION_TYPE: ParamsType = "cursor"

    BASE_DIR: Path = Path(__file__).parent.parent
    APP_DIR: Path = BASE_DIR / 'app'
    CORE_DIR: Path = BASE_DIR / 'core'

settings = Settings()
