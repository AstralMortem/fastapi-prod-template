from unittest.mock import patch, AsyncMock, Mock, MagicMock

from fastapi import Depends, FastAPI
from starlette.testclient import TestClient

from core.security.permission import Authorization, HasPermission, HasRole
from core.controller import as_route, Controller

def test_class():

    class AuthTestController(Controller):

        @as_route("/login", method="POST")
        def login_route(self, user = Depends(HasPermission("write") | HasRole("ADMIN"))):
            return user


    router = AuthTestController.as_router()
    app = FastAPI()
    app.include_router(router)



    with patch("core.security.permission.AuthService") as mocked_service:
        mocked_service = MagicMock()
        mocked_service.authorize = AsyncMock().side_effect = lambda x,y : Mock(id=1)
        client = TestClient(app, headers={"Authorization": "Bearer token"})

        res = client.post('/login')
        print(res.json())
        assert res.status_code == 200

