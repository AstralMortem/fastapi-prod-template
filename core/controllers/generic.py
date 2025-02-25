import inspect
from typing import get_type_hints, Callable, ClassVar
from fastapi.params import Depends as DependsClass, Path as PathClass
from fastapi import APIRouter, HTTPException, Path, FastAPI, Depends
from makefun import with_signature
from pydantic.v1.typing import is_classvar
from fastapi.routing import APIRoute

HTTP_ACTIONS = {
    'get': "GET",
    'list': "GET",
    'post': "POST",
    'patch': "PATCH",
    'put': "PUT",
    'delete': 'DELETE'
}

CBV_CLASS_PREFIX = '__CBV__'
CBV_CUSTOM_ROUTE_PREFIX = '__CBV_CUSTOM_ROUTE__'



class Controller:
    router_prefix: ClassVar[str] = "/"
    router_tags: ClassVar[list[str]] = []

    # async def get(self, id: int):
    #     pass
    #
    # async def post(self, data: dict):
    #     pass
    #
    # async def list(self, pagination: dict, filters: dict):
    #     pass
    #
    # async def patch(self, id: int, data: dict):
    #     pass
    #
    # async def put(self, id: int, data: dict):
    #     pass
    #
    # async def delete(self, id: int):
    #     pass
    #
    # async def test(self):
    #     pass

    @classmethod
    def as_view(cls, exceptions: dict[str, HTTPException]  | None = None):
        router = APIRouter(
            tags=cls.router_tags or [cls.__name__])
        cls._init_view()

        for attr_name, attr in inspect.getmembers(cls, inspect.iscoroutinefunction):
            if attr_name.lower() in HTTP_ACTIONS or hasattr(attr, CBV_CLASS_PREFIX):
                router.routes.append(
                    cls._generate_route(attr)
                )


        return router


    @classmethod
    def _init_view(cls):
        if getattr(cls, CBV_CLASS_PREFIX, False):
            return
        old_init = cls.__init__
        old_signature = inspect.signature(old_init)
        old_params = list(old_signature.parameters.values())[1:]
        new_params = [
            x for x in old_params if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]

        dep_names: list[str] = []
        for name, hint in get_type_hints(cls).items():
            if is_classvar(hint):
                continue
            dep_names.append(name)
            new_params.append(
                inspect.Parameter(
                    name= name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=hint,
                    default=getattr(cls, name, Ellipsis)
                )
            )

        new_params = [inspect.Parameter(
            name='self',
            kind=inspect.Parameter.POSITIONAL_ONLY,
            annotation=cls,
        )] + new_params

        new_signature = old_signature.replace(parameters=new_params)

        @with_signature(new_signature)
        def new_init(self, *args, **kwargs):
            for dep_name in dep_names:
                setattr(self, dep_name, kwargs.pop(dep_name))

        # setattr(cls, "__signature__", new_signature)
        setattr(cls,"__init__", new_init)
        setattr(cls, CBV_CLASS_PREFIX, True)

    @classmethod
    def _generate_route(cls, func: Callable):

        attr_signature = inspect.signature(func).parameters

        paths = []

        for param in attr_signature.values():
            if param.name == 'self':
                continue
            if param.annotation is dict:
                continue
            if isinstance(param.default, DependsClass):
                continue


            paths.append('/{' + param.name + '}')

        route = APIRoute(
            path = cls.router_prefix + "".join(paths) if paths else cls.router_prefix,
            endpoint=func,
            methods=[HTTP_ACTIONS[func.__name__.lower()]],
            name=f'{cls.__name__}.{func.__name__}'
        )

        old_params = list(inspect.signature(route.endpoint).parameters.values())
        route_self = old_params[0]
        new_self = route_self.replace(default=Depends(cls))
        new_params = [new_self] + [parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_params[1:]]
        new_signature = inspect.Signature(new_params)
        setattr(route.endpoint, '__signature__', new_signature)
        return route
