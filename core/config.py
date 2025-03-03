import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, MariaDBDsn, MySQLDsn
from fastapi_pagination.types import ParamsType


class Settings(BaseSettings):
    DEBUG: bool = True

    # Database Section
    DATABASE_URL: PostgresDsn | MariaDBDsn | MySQLDsn | str = (
        "sqlite+aiosqlite:///test.db"
    )
    SQLALCHEMY_ENGINE_CONFIG: dict[str, Any] = {}
    DEFAULT_PK_FIELD_NAME: str | None = "id"
    DEFAULT_PK_FIELD_TYPE: type[str] | type[int] | type[uuid.UUID] = int
    PAGINATION_TYPE: ParamsType = "cursor"

    # Files Section
    BASE_DIR: Path = Path(__file__).parent.parent
    APP_DIR: Path = BASE_DIR / "app"
    CORE_DIR: Path = BASE_DIR / "core"

    # Router Section
    GLOBAL_ROUTER_PREFIX: str = "/api"

    # Auth Section
    USER_LOGIN_FIELDS: list[str] = ["email"]
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_MAX_AGE: int = 60 * 60 * 12  # 12 hours
    JWT_REFRESH_TOKEN_MAX_AGE: int = 60 * 60 * 24 * 12  # 12 days
    JWT_AUTH_AUDIENCE: str = "auth"
    ALLOW_LOGIN_FIELDS_IN_JWT_TOKEN: bool = False
    AUTH_METHOD: Literal["cookie", "header"] = "cookie"

    AUTH_ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    AUTH_REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    AUTH_COOKIE_PATH: str | None = "/"
    AUTH_COOKIE_DOMAIN: str | None = None
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_HTTPONLY: bool = False
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = "lax"
    LOGIN_URL: str = "/api/v1/auth/login"
    USER_IS_ACTIVE_DEFAULT: bool = True
    USER_DEFAULT_ROLE_NAME: str | None = 'USER'


settings = Settings()
