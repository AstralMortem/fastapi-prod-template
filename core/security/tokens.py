from app.models.auth import User
from core.config import settings
from core.utils.jwt_helper import encode_token
from fastapi.responses import Response, JSONResponse
from fastapi import status

def generate_access_token(user: User):
    payload = {
        "sub": str(user.id),
        "type": 'access'
    }
    if settings.ALLOW_LOGIN_FIELDS_IN_JWT_TOKEN:
        for field in settings.USER_LOGIN_FIELDS:
            user_field = getattr(user, field, None)
            if user_field:
                payload[field] = user_field

    return encode_token(payload, settings.JWT_ACCESS_TOKEN_MAX_AGE, settings.JWT_AUTH_AUDIENCE)

def generate_refresh_token(user: User):
    payload = {
        "sub": str(user.id),
        "type": 'refresh'
    }
    return encode_token(payload, settings.JWT_REFRESH_TOKEN_MAX_AGE, settings.JWT_AUTH_AUDIENCE)

def _create_cookie(key:str, value:str, max_age:int, response: Response | None = None):
    if response is None:
        response = Response(status.HTTP_204_NO_CONTENT)
    response.set_cookie(
            key=key,
            value=value,
            max_age=max_age,
            path=settings.AUTH_COOKIE_PATH,
            domain=settings.AUTH_COOKIE_DOMAIN,
            secure=settings.AUTH_COOKIE_SECURE,
            httponly=settings.AUTH_COOKIE_HTTPONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE
    )
    return response

def generate_tokens_response(user: User):
    if settings.AUTH_METHOD == "cookie":
        response = _create_cookie(
            settings.AUTH_ACCESS_TOKEN_COOKIE_NAME,
            generate_access_token(user),
            settings.JWT_ACCESS_TOKEN_MAX_AGE
        )
        response = _create_cookie(
            settings.AUTH_REFRESH_TOKEN_COOKIE_NAME,
            generate_refresh_token(user),
            settings.JWT_REFRESH_TOKEN_MAX_AGE,
            response
        )
        return response

    if settings.AUTH_METHOD == "header":
        payload = {
            "access_token": generate_access_token(user),
            "refresh_token": generate_refresh_token(user),
            "type": 'bearer'
        }
        return JSONResponse(
            content=payload,
            status_code=status.HTTP_200_OK,
        )


