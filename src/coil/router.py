from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import insert, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker

from src.coil.models import Coil
from src.coil.schemas import CoilSchemaCreate, BaseCoilSchema, CoilSchemaRead, CoilSchemaGetParams, DateRangeSchema
from src.coil.servises import coil_exists, is_coil_deleted


router = APIRouter(
    prefix='/api/coil',
    tags=["Coil"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coil(new_coil: CoilSchemaCreate, session: AsyncSession = Depends(get_async_session)) -> BaseCoilSchema:
    statement = insert(Coil).values(**new_coil.model_dump()).returning(Coil.id)
    result = await session.execute(statement)
    await session.commit()

    id = result.scalar()

    return BaseCoilSchema(id=id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coil(id: int, session: AsyncSession = Depends(get_async_session)):
    if not await coil_exists(id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": f"Coil with {id=} not found"})
    elif await is_coil_deleted(id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": f"Coil with {id=} was already deleted"})

    statement = update(Coil).where(Coil.id == id).values(deleted_at=datetime.utcnow())
    await session.execute(statement)
    await session.commit()

@router.get("/")
async def get_coil(
    range_params: CoilSchemaGetParams = Depends(CoilSchemaGetParams),
    session: AsyncSession = Depends(get_async_session)
) -> list[CoilSchemaRead]:
    range_params: dict = range_params.model_dump(exclude_none=True)
    
    filters = [
        and_(
            getattr(Coil, from_field.replace('from_', '', 1)) >= range_params[from_field],
            getattr(Coil, to_field.replace('to_', '', 1)) <= range_params[to_field]
        )
        for from_field, to_field in CoilSchemaGetParams.dependant_fields.items() if range_params.get(from_field)
    ]
    
    query = select(Coil).where(and_(*filters))
    result = await session.execute(query)

    coils = [
        CoilSchemaRead(
            id=coil[0].id,
            length=coil[0].length,
            weight=coil[0].weight,
            created_at=coil[0].created_at,
            deleted_at=coil[0].deleted_at,

        )
        for coil in result.all()
    ]

    return coils

@router.get("/stats")
async def get_coil_stats(
    date_range: DateRangeSchema = Depends(DateRangeSchema),
    session: AsyncSession = Depends(get_async_session)
):
    pass
