import uuid

from core.config import settings
from core.schema import ReadSchema, WriteSchema, UpdateSchema


class UserReadSchema(ReadSchema):
    id: uuid.UUID



class UserCreateSchema(WriteSchema):
    email: str
    password: str

class UserUpdateSchema(UpdateSchema):
    email: str | None = None


class RoleReadSchema(ReadSchema):
    id: settings.DEFAULT_PK_FIELD_TYPE
    codename:str

class RoleCreateSchema(WriteSchema):
    codename: str

class RoleUpdateSchema(UpdateSchema):
    codename: str | None = None