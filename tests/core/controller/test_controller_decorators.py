import inspect

from fastapi import FastAPI
from fastapi.routing import APIRoute
from typing import Generic, TypeVar

from pydantic import BaseModel
from starlette.testclient import TestClient

from core.controller.base import Controller, as_route, CONTROLLER_ROUTE_PREFIX


class ControllerWithRoutes(Controller):
    pass


TEST = TypeVar("TEST")


def test_prefix_set():
    def f():
        return None

    assert not hasattr(f, CONTROLLER_ROUTE_PREFIX)
    f = as_route("/", method="GET")(f)
    assert hasattr(f, CONTROLLER_ROUTE_PREFIX)


def test_apiroute_return():
    def func():
        return None

    f = as_route("/", method="GET")(func)

    route = f(ControllerWithRoutes)
    assert isinstance(route, APIRoute)  # Need to pass cls, to which this route belong
    assert route.path == "/"
    assert route.methods == {"GET"}
    assert route.endpoint is func


def test_apiroute_typevar_support():
    class ControllerWithGeneric(Controller, Generic[TEST]):
        @as_route("/", method="GET", override_args=("test", TEST))
        def f(self, test):
            return None

    # Generic types resolves only when generic class inherited with set type
    class SubController(ControllerWithGeneric[int]):
        pass

    router = SubController.as_router()
    sig = inspect.signature(router.routes[0].endpoint)
    assert sig.parameters.get("test").annotation == int


def test_apiroute_typevar_response_model():
    class ControllerWithGeneric(Controller, Generic[TEST]):
        @as_route("/", method="GET", response_model=TEST)
        def f(self):
            class ReturnClass:
                test = "test"

            return ReturnClass()

    class ResponseModel(BaseModel):
        test: str

    class SubController(ControllerWithGeneric[ResponseModel]):
        pass

    router = SubController.as_router()

    assert router.routes[0].response_model is ResponseModel
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == ResponseModel(test="test").model_dump()
