from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker

from src.coil.models import Coil
from src.coil.schemas import CoilSchemaCreate, BaseCoilSchema
from src.coil.servises import coil_exists


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coil with {id=} not found")

    statement = delete(Coil).where(Coil.id == id)
    await session.execute(statement)
    await session.commit()
