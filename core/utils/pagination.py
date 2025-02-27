from core.config import settings
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate

if settings.PAGINATION_TYPE == "cursor":
    from fastapi_pagination import Params, Page

    Params = Params
    Page = Page
else:
    from fastapi_pagination import LimitOffsetPage, LimitOffsetParams

    Params = LimitOffsetParams
    Page = LimitOffsetPage

__all__ = ["Params", "Page", "AbstractParams", "AbstractPage", "paginate"]
