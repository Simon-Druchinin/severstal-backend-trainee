from typing import Optional
from datetime import datetime, date, timedelta

from pydantic import BaseModel, model_validator, PositiveInt

from fastapi.exceptions import RequestValidationError

from src.coil.utils import date_to_datetime


class BaseCoilSchema(BaseModel):
    id: int

class CoilSchemaCreate(BaseModel):
    length: PositiveInt
    weight: PositiveInt

class CoilSchemaRead(CoilSchemaCreate, BaseCoilSchema):
    created_at: datetime
    deleted_at: Optional[datetime] = None

class DateRangeSchema(BaseModel):
    from_date: date | datetime
    to_date: date | datetime
    
    @model_validator(mode='after')
    def validate_fields_dependency(cls, field_values):
        for field_name in cls.__fields__.keys():
            value = getattr(field_values, field_name)
            if isinstance(value, date):
                formated_date = date_to_datetime(value, field_name.startswith("to_"))
                setattr(field_values, field_name, formated_date)
        if field_values.from_date > field_values.to_date:
            raise RequestValidationError("from_date is greater than to_date")
        return field_values
        

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
                    data[from_field] = date_to_datetime(data[from_field], from_field.startswith("to_"))
                    setattr(field_values, from_field, data[from_field])

                if isinstance(data[to_field], date):
                    data[to_field] = date_to_datetime(data[to_field], to_field.startswith("to_"))
                    setattr(field_values, to_field, data[to_field])

                if data[from_field] > data[to_field]:
                    raise RequestValidationError(f"{from_field} is greater than {to_field}")
                
        return field_values

class CoilStatsSchema(BaseModel):
    amount: int
    deleted_amount: int
    average_length: float
    average_weight: float
    max_length: int
    min_length: int
    max_weight: int
    min_weight: int
    total_weight: int
    creation_max_time_gap: Optional[timedelta | str] = None
    creation_min_time_gap: Optional[timedelta | str] = None
    deletion_max_time_gap: Optional[timedelta | str] = None
    deletion_min_time_gap: Optional[timedelta | str] = None
    max_amount_day: date
    min_amount_day: date
    max_total_weight_day: date
    min_total_weight_day: date

    @model_validator(mode='after')
    def validate_fields_dependency(cls, field_values):
        for field_name in cls.__fields__.keys():
            value = getattr(field_values, field_name)
            if isinstance(value, timedelta):
                setattr(field_values, field_name, str(value))

        return field_values
