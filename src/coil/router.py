from fastapi import APIRouter, Depends, status

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker

from src.coil.models import Coil
from src.coil.schemas import CoilSchemaCreate, BaseCoilSchema


router = APIRouter(
    prefix='/api/coil',
    tags=["Coil"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coil(new_coil: CoilSchemaCreate, session: AsyncSession = Depends(get_async_session)) -> BaseCoilSchema:
    statement = insert(Coil).values(**new_coil.model_dump()).returning(Coil.id)
    result = await session.execute(statement)
    await session.commit()

    id = result.first()[0]

    return BaseCoilSchema(id=id)
