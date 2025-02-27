import pytest
from unittest.mock import AsyncMock, patch
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from core.config import settings
from core.security.permission import (
    _get_access_token,
    authorize,
    access_token_required,
    refresh_token_required,
)


def test_get_access_token_cookie():
    settings.AUTH_METHOD = "cookie"
    token_dep = _get_access_token()
    assert isinstance(token_dep, APIKeyCookie)
    assert token_dep.model.name == settings.AUTH_ACCESS_TOKEN_COOKIE_NAME


def test_get_access_token_header():
    settings.AUTH_METHOD = "header"
    token_dep = _get_access_token()
    assert isinstance(token_dep, OAuth2PasswordBearer)
    assert token_dep.model.flows.password.tokenUrl == settings.LOGIN_URL


@pytest.mark.asyncio
async def test_authorize():
    mock_service = AsyncMock()
    mock_service.authorize.return_value = "authorized"
    with patch("core.security.permission.get_auth_service", return_value=mock_service):
        auth_func = authorize()
        result = await auth_func("mock_token", mock_service)
    assert result == "authorized"
    mock_service.authorize.assert_called_once_with("mock_token", "access")


@pytest.mark.asyncio
async def test_access_token_required():
    mock_service = AsyncMock()
    mock_service.authorize.return_value = "authorized"
    with patch("core.security.permission.get_auth_service", return_value=mock_service):
        auth_func = access_token_required()
        result = await auth_func("mock_token", mock_service)
    assert result == "authorized"
    mock_service.authorize.assert_called_once_with("mock_token", "access")


@pytest.mark.asyncio
async def test_refresh_token_required():
    mock_service = AsyncMock()
    mock_service.authorize.return_value = "authorized"
    with patch("core.security.permission.get_auth_service", return_value=mock_service):
        auth_func = refresh_token_required()
        result = await auth_func("mock_token", mock_service)
    assert result == "authorized"
    mock_service.authorize.assert_called_once_with("mock_token", "refresh")
