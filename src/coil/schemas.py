from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, model_validator, PositiveInt

from fastapi.exceptions import RequestValidationError


class BaseCoilSchema(BaseModel):
    id: int

class CoilSchemaCreate(BaseModel):
    length: PositiveInt
    weight: PositiveInt

class CoilSchemaRead(CoilSchemaCreate, BaseCoilSchema):
    created_at: datetime
    deleted_at: Optional[datetime] = None

class CoilSchemaGetParams(BaseModel):
    from_id: Optional[PositiveInt] = None
    to_id: Optional[PositiveInt] = None 
    from_weight: Optional[PositiveInt] = None
    to_weight: Optional[PositiveInt] = None
    from_length: Optional[PositiveInt] = None
    to_length: Optional[PositiveInt] = None
    from_created_at: Optional[date | datetime] = None
    to_created_at: Optional[date | datetime] = None
    from_deleted_at: Optional[date | datetime] = None
    to_deleted_at: Optional[date | datetime] = None


    @staticmethod
    def date_to_datetime(field_value: date, to_max_time: bool = False) -> datetime:
        time = datetime.max.time() if to_max_time else datetime.min.time()
        field_value = datetime.combine(field_value, time)
        return field_value

    @classmethod
    @property
    def dependant_fields(cls):
        return {
            "from_id": "to_id",
            "from_weight": "to_weight",
            "from_length": "to_length",
            "from_created_at": "to_created_at",
            "from_deleted_at": "to_deleted_at",
        }

    @model_validator(mode='after')
    def validate_fields_dependency(cls, field_values):
        data = dict(field_values)

        if not any(data.values()):
            raise RequestValidationError(f"None of fields is specified")

        for from_field, to_field in cls.dependant_fields.items():
            if any([data[from_field], data[to_field]]) and not all([data[from_field], data[to_field]]):
                raise RequestValidationError(f"One of fields is missed: {from_field} or {to_field}")
            
            if data[from_field] and data[to_field]:
                if isinstance(data[from_field], date):
                    data[from_field] = cls.date_to_datetime(data[from_field], from_field.startswith("to_"))
                    setattr(field_values, from_field, data[from_field])

                if isinstance(data[to_field], date):
                    data[to_field] = cls.date_to_datetime(data[to_field], to_field.startswith("to_"))
                    setattr(field_values, to_field, data[to_field])

                if data[from_field] > data[to_field]:
                    raise RequestValidationError(f"{from_field} is greater than {to_field}")
                
        return field_values

