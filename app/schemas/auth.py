import uuid

from core.schema import ReadSchema, WriteSchema

class UserReadSchema(ReadSchema):
    id: uuid.UUID



class UserCreateSchema(WriteSchema):
    email: str
    password: str

