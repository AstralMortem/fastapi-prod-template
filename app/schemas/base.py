from pydantic import BaseModel, ConfigDict

class ReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class WriteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)