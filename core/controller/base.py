import inspect
import typing
from contextlib import asynccontextmanager
from typing import (
    Literal,
    ClassVar,
    get_type_hints,
    Optional,
    Any,
    List,
    Union,
    Sequence,
    Dict,
    Type,
    Callable,
)
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.routing import APIRoute
from fastapi import APIRouter, FastAPI, Depends, params, Response
from fastapi.params import Depends as DependClass
from enum import Enum
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id
from makefun import with_signature
from mashumaro.core.meta.helpers import resolve_type_params
from pydantic.v1.typing import is_classvar
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from typing import TypeVar

from core.security.permission import Authorization, Authorize
from core.utils.string import snake2camel

HTTP_METHOD = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
CONTROLLER_ROUTE_PREFIX = "__CONTROLLER_ROUTE__"
CONTROLLER_CLASS_PREFIX = "__CONTROLLER_CLASS__"


def _get_typevar_class(cls: type["Controller"], typevar: any):
    # Resolve typevar from generic
    type_param = resolve_type_params(cls)
    for key, val in type_param.items():
        if val:
            return val[typevar]


def _override_signatures(
    cls: type["Controller"],
    func,
    overrides: tuple[str, TypeVar] | list[tuple[str, TypeVar]] | None = None,
):
    if overrides is not None:
        # Get old signature
        old_signatures = inspect.signature(func)
        old_params = old_signatures.parameters
        old_params_list = list(old_params.values())

        # If in format tuple[str, TypeVar] where str is argument name
        if type(overrides) == tuple:
            target_param = old_params.get(overrides[0], None)
            if target_param is not None:
                idx = old_params_list.index(target_param)
                old_params_list[idx] = target_param.replace(
                    annotation=_get_typevar_class(cls, overrides[1])
                )
        # If in format list[tuple[str, TypeVar]]
        elif type(overrides) == list:
            for override in overrides:
                target_param = old_params.get(override[0], None)
                if target_param is not None:
                    idx = old_params_list.index(target_param)
                    old_params_list[idx] = target_param.replace(
                        annotation=_get_typevar_class(cls, override[1])
                    )
        else:
            return func

        new_signature = old_signatures.replace(parameters=old_params_list)
        # With makefun convert to new signature
        return with_signature(new_signature)(func)
    return func

def _override_authorization_class(cls: type["Controller"], func):
    old_signature = inspect.signature(func)
    params = list(old_signature.parameters.values())
    for param in params:
        if isinstance(param.default, Authorize):
            idx = params.index(param)
            params[idx] = param.replace(default=Depends(param.default.as_dependency(cls)))
            break
    new_signature = old_signature.replace(parameters=params)
    return with_signature(new_signature)(func)

def _override_response_model(cls: type["Controller"], response_model):
    # Check if response model is typevar
    if response_model and type(response_model) == typing.TypeVar:
        return _get_typevar_class(cls, response_model)
    # Check if response model is Cast class and typevar, used for Page[TypeVar] pydantic model
    elif response_model and type(response_model) == tuple:
        return response_model[0][
            _get_typevar_class(cls, response_model[1])
        ]
    else:
        return response_model


def _parse_global_dependencies(cls: type["Controller"], dependencies: Optional[Sequence[params.Depends] | Sequence[Authorize]] = None):
    resolved_dependencies = []
    if dependencies is not None:
        for dependency in dependencies:
            if isinstance(dependency, Authorize):
                resolved_dependencies.append(Depends(dependency.as_dependency(cls)))
            else:
                resolved_dependencies.append(dependency)
    return resolved_dependencies

def as_route(
    path: str,
    method: HTTP_METHOD,
    *,
    override_args: tuple[str, typing.TypeVar]
    | list[tuple[str, typing.TypeVar]]
    | None = None,
    response_model: Any = Default(None),
    status_code: Optional[int] = None,
    tags: Optional[List[Union[str, Enum]]] = None,
    dependencies: Optional[Sequence[params.Depends] | Sequence[Authorize]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    response_description: str = "Successful Response",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    deprecated: Optional[bool] = None,
    name: Optional[str] = None,
    operation_id: Optional[str] = None,
    response_model_include: Optional[IncEx] = None,
    response_model_exclude: Optional[IncEx] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: Union[Type[Response], DefaultPlaceholder] = Default(JSONResponse),
    dependency_overrides_provider: Optional[Any] = None,
    callbacks: Optional[List[BaseRoute]] = None,
    openapi_extra: Optional[Dict[str, Any]] = None,
    generate_unique_id_function: Union[
        Callable[["APIRoute"], str], DefaultPlaceholder
    ] = Default(generate_unique_id),
):
    def decorator(function):
        """Main decorator which decorate class method set controller prefix and return APIRoute for method"""

        def wrapper(cls: type[Controller], *args, **kwargs):
            endpoint = _override_signatures(cls, function, override_args)
            endpoint = _override_authorization_class(cls, endpoint)

            return APIRoute(
                path=path,
                endpoint=endpoint,
                methods=[method],
                status_code=status_code,
                tags=tags or [cls.__name__],
                dependencies=_parse_global_dependencies(cls, dependencies),
                summary=summary,
                description=description,
                deprecated=deprecated,
                operation_id=operation_id,
                name=name or f"{cls.__name__}.{snake2camel(function.__name__)}",
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                responses=responses,
                response_description=response_description,
                response_model=_override_response_model(cls,response_model),
                response_class=response_class,
                dependency_overrides_provider=dependency_overrides_provider,
                callbacks=callbacks,
                openapi_extra=openapi_extra,
                generate_unique_id_function=generate_unique_id_function,
            )

        setattr(wrapper, CONTROLLER_ROUTE_PREFIX, True)
        return wrapper

    return decorator


class Controller:
    router_prefix: ClassVar[str] = ""
    router_tags: ClassVar[list[str | Enum] | None] = None
    router_responses: ClassVar[dict | None] = None
    router_callbacks: ClassVar[list[BaseRoute]] = None
    global_dependencies: ClassVar[list[DependClass] | None] = None
    is_deprecated: ClassVar[bool] = False
    resource_name: ClassVar[str | None] = None

    @staticmethod
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield

    @classmethod
    def as_router(cls):
        router = APIRouter(
            prefix=cls.router_prefix,
            tags=cls.router_tags,
            lifespan=cls.lifespan,
            dependencies=_parse_global_dependencies(cls, cls.global_dependencies),
            callbacks=cls.router_callbacks,
            responses=cls.router_responses,
            deprecated=cls.is_deprecated,
        )

        cls.__init_dependencies()
        cls.__init_routers(router)
        return router

    @classmethod
    def __init_dependencies(cls):
        if getattr(cls, CONTROLLER_CLASS_PREFIX, False):
            return

        # get old init signature
        old_signature = inspect.signature(cls.__init__)
        old_params = list(old_signature.parameters.values())[1:]
        new_params = [
            x
            for x in old_params
            if x.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]

        dep_names: list[str] = []
        for name, hint in get_type_hints(cls).items():
            if is_classvar(hint):
                continue
            dep_names.append(name)
            new_params.append(
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=hint,
                    default=getattr(cls, name, Ellipsis),
                )
            )

        new_params = [
            inspect.Parameter(
                name="self",
                kind=inspect.Parameter.POSITIONAL_ONLY,
                annotation=cls,
            )
        ] + new_params

        new_signature = old_signature.replace(parameters=new_params)

        @with_signature(new_signature)
        def new_init(self, *args, **kwargs):
            for dep_name in dep_names:
                setattr(self, dep_name, kwargs.pop(dep_name))

        setattr(cls, "__init__", new_init)
        setattr(cls, CONTROLLER_CLASS_PREFIX, True)

    @classmethod
    def __init_routers(cls, router: APIRouter):
        for attr_name, attr in inspect.getmembers(cls, inspect.isfunction):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            if CONTROLLER_ROUTE_PREFIX in dir(attr):
                route: APIRoute = attr(cls)
                old_route_signature = inspect.signature(route.endpoint)
                old_route_params = list(old_route_signature.parameters.values())
                new_self_param = old_route_params[0].replace(default=Depends(cls))
                new_params = [new_self_param] + [
                    parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
                    for parameter in old_route_params[1:]
                ]

                new_signature = inspect.Signature(new_params)
                route.endpoint = with_signature(new_signature)(route.endpoint)
                route.path = router.prefix + route.path
                router.routes.append(route)
        return router
