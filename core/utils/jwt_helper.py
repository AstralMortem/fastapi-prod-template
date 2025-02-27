from datetime import datetime, UTC, timedelta
from core.config import settings
import jwt
from jwt import DecodeError


def decode_token(token: str, audience: str | list[str] | None = None, **kwargs):
    return jwt.decode(
        token,
        key=settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        audience=audience,
        **kwargs,
    )


def encode_token(
    payload: dict[str, any],
    max_age: int | None,
    audience: str | list[str] | None = None,
    **kwargs,
):
    payload["aud"] = payload.get("aud", audience)
    iat = payload.get("iat", datetime.now(UTC))
    payload["iat"] = iat
    payload["exp"] = (
        payload.get("exp", iat + timedelta(seconds=max_age)) if max_age else None
    )

    return jwt.encode(
        payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM, **kwargs
    )
