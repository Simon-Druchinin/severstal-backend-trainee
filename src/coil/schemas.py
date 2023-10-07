from pydantic import BaseModel

class MessageSchemaCreate(BaseModel):
    message: str
    client_id: int

class MessageSchemaView(MessageSchemaCreate):
    id: int
