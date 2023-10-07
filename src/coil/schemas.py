from pydantic import BaseModel


class BaseCoilSchema(BaseModel):
    id: int

class CoilSchemaCreate(BaseModel):
    length: int
    weight: int

class CoilSchemaRead(BaseCoilSchema, CoilSchemaCreate):
    pass
