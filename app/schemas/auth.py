from core.schema import ReadSchema,WriteSchema

class UserCreateSchema(WriteSchema):
    email: str
    password: str