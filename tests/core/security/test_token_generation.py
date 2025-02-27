import json
from unittest.mock import Mock, patch
from fastapi.responses import Response, JSONResponse
from core.config import settings
from core.security.tokens import (
    generate_access_token,
    generate_refresh_token,
    generate_tokens_response,
)


def test_generate_access_token():
    user = Mock(id=1, email="test@example.com")
    with patch("core.security.tokens.encode_token", return_value="mocked_access_token"):
        token = generate_access_token(user)
    assert token == "mocked_access_token"


def test_generate_refresh_token():
    user = Mock(id=1)
    with patch(
        "core.security.tokens.encode_token", return_value="mocked_refresh_token"
    ):
        token = generate_refresh_token(user)
    assert token == "mocked_refresh_token"


# def test_create_cookie():
#     response = _create_cookie("test_cookie", "test_value", 100)
#     print(response)
#     assert isinstance(response, Response)
#     assert response.headers["set-cookie"].startswith("test_cookie=test_value;")


def test_generate_tokens_response_header():
    user = Mock(id=1, email="test@example.com")
    settings.AUTH_METHOD = "header"
    with (
        patch(
            "core.security.tokens.generate_access_token",
            return_value="mocked_access_token",
        ),
        patch(
            "core.security.tokens.generate_refresh_token",
            return_value="mocked_refresh_token",
        ),
    ):
        response = generate_tokens_response(user)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert json.loads(response.body) == {
        "access_token": "mocked_access_token",
        "refresh_token": "mocked_refresh_token",
        "token_type": "bearer",
    }


def test_generate_tokens_response_cookie():
    user = Mock(id=1)
    settings.AUTH_METHOD = "cookie"
    with (
        patch(
            "core.security.tokens.generate_access_token",
            return_value="mocked_access_token",
        ),
        patch(
            "core.security.tokens.generate_refresh_token",
            return_value="mocked_refresh_token",
        ),
        patch(
            "core.security.tokens._create_cookie",
            side_effect=lambda k, v, m, r=None: Response(),
        ) as mock_cookie,
    ):
        response = generate_tokens_response(user)
    assert isinstance(response, Response)
    assert mock_cookie.call_count == 2
