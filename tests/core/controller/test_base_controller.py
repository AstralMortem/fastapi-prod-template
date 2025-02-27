import inspect
from fastapi.testclient import TestClient
from core.controller.base import Controller, as_route, CONTROLLER_CLASS_PREFIX
from fastapi import FastAPI, Depends, APIRouter
from fastapi.params import Depends as DependClass
from fastapi.routing import APIRoute


async def dependency_for_test():
    return "test"


class ControllerWithRoutes(Controller):
    dependency: str = Depends(dependency_for_test)

    @as_route("/", method="GET")
    def test_route(self):
        return self.dependency

    @as_route("/", method="POST")
    async def async_test_route(self):
        return self.dependency


def test_init_dependencies():
    # Check if class not inited
    cls = ControllerWithRoutes
    assert not hasattr(cls, CONTROLLER_CLASS_PREFIX)

    # Check if dependency not resolved
    instance = cls()
    assert not isinstance(instance.dependency, str)

    # Init dependency
    cls._Controller__init_dependencies()
    # Check if class inited
    assert hasattr(cls, CONTROLLER_CLASS_PREFIX)

    # Check if dependency in __init__ args and has Depends class as default
    dependency_param = inspect.signature(cls.__init__).parameters.get(
        "dependency", False
    )
    assert dependency_param
    assert isinstance(dependency_param.default, DependClass)


def test_routers_registration():
    test_router = APIRouter()

    # Init dependencies
    cls = ControllerWithRoutes
    cls._Controller__init_dependencies()

    # Register router
    cls._Controller__init_routers(test_router)

    assert len(test_router.routes) == 2
    assert isinstance(test_router.routes[0], APIRoute)
    assert isinstance(test_router.routes[1], APIRoute)


def test_controller_as_router():
    app = FastAPI()
    router = ControllerWithRoutes.as_router()
    app.include_router(router)
    client = TestClient(app)

    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == "test"  # Because return resolved dependency value

    res = client.post("/")
    assert res.status_code == 200
    assert res.json() == "test"
