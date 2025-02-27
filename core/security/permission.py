from enum import StrEnum

from typing import Literal
from fastapi import Depends
from app.models.auth import User
from core.config import settings
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from core.types import TokenType
from app.services.auth import get_auth_service, AuthService
from core.utils.string import camel2snake

def _get_access_token():
    if settings.AUTH_METHOD == "cookie":
        return APIKeyCookie(name=settings.AUTH_ACCESS_TOKEN_COOKIE_NAME, auto_error=True)
    if settings.AUTH_METHOD == "header":
        return OAuth2PasswordBearer(settings.LOGIN_URL, auto_error=True)


def authenticate(token_type: TokenType = "access"):
    async def _authenticate(
        token: str = Depends(_get_access_token()),
        service: AuthService = Depends(get_auth_service),
    ):
        return await service.authorize(token, token_type)
    return _authenticate


def access_token_required():
    return authenticate("access")


def refresh_token_required():
    return authenticate("refresh")

class Actions(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"

class Authorization:
    resource_name: str

    def has_access(self, user: User) -> User:
        raise NotImplementedError

    def __or__(self, other: "Authorization"):
        return _OR(self, other)

    def __and__(self, other):
        return _AND(self, other)

    def __call__(self):
        return None


class _OR(Authorization):
    def __init__(self, left: Authorization, right: Authorization):
        self.left = left
        self.right = right

    def has_access(self, user: User):
        return self.left.has_access(user) or self.right.has_access(user)

    def __repr__(self):
        return f"({self.left} | {self.right})"

class _AND(Authorization):
    def __init__(self, left: Authorization, right: Authorization):
        self.left = left
        self.right = right

    def has_access(self, user: User):
        return self.left.has_access(user) and self.right.has_access(user)

    def __repr__(self):
        return f"({self.left} & {self.right})"

class HasPermission(Authorization):

    def __init__(self, action: Actions | str | Literal["*"]):
        self.action = action

    def concat_permission(self):
        if ":" in self.action:
            return self.action
        return f"{self.resource_name}:{self.action}"

    def has_access(self, user: User) -> User | bool:
        permissions = []
        # Convert permission to list of codenames
        for role in user.roles:
            permissions.extend(list(map(lambda x: x.codename, role.permissions)))
        permissions = set(permissions)

        # check if full permission in user permissions list
        check_permission = self.concat_permission()
        if check_permission in permissions:
            return user
        # if action is * get permission which starts with resource name
        if self.action == "*":
            valid = any([perm.startswith(self.resource_name) for perm in permissions])
            if valid:
                return user
        return False


class HasRole(Authorization):
    def __init__(self, role: str):
        self.role = role

    def has_access(self, user: User) -> User | bool:
        role_names = list(map(lambda x: str(x.codename).lower(), user.roles))
        if self.role.lower() in role_names:
            return user
        return False


class Authorize:

    def __init__(self, scope: Authorization, token_type: TokenType = "access"):
        self.scope = scope
        self.token_type = token_type

    def as_dependency(self, controller_class):
        async def _as_dependency(user: User = Depends(authenticate(self.token_type))):
            resource_name = controller_class.resource_name or camel2snake(controller_class.__name__)
            if hasattr(self.scope, "left"):
                self.scope.left.resource_name = resource_name
            if hasattr(self.scope, "right"):
                self.scope.right.resource_name = resource_name
            return self.scope.has_access(user)
        return _as_dependency