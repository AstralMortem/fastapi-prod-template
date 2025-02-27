from fastapi import Depends
from core.config import settings
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from core.types import TokenType
from app.services.auth import get_auth_service, AuthService


def _get_access_token():
    if settings.AUTH_METHOD == "cookie":
        return APIKeyCookie(name=settings.AUTH_ACCESS_TOKEN_COOKIE_NAME)
    if settings.AUTH_METHOD == "header":
        return OAuth2PasswordBearer(settings.LOGIN_URL)

def authorize(token_type: TokenType = "access"):
    async def _authorize(token: str = Depends(_get_access_token()), service: AuthService = Depends(get_auth_service)):
        return await service.authorize(token, token_type)
    return _authorize

def access_token_required():
    return authorize("access")

def refresh_token_required():
    return authorize("refresh")




