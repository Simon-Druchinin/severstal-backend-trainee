from sqlalchemy import exists, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.coil.models import Coil


async def coil_exists(id: int, session: AsyncSession) -> bool:
    query = select(exists().where(Coil.id == id))
    result = await session.execute(query)
    
    return result.scalar()

async def is_coil_deleted(id: int, session: AsyncSession) -> bool:
    query = select(exists().where(and_(Coil.id == id, Coil.deleted_at.isnot(None))))
    result = await session.execute(query)
    
    return result.scalar()
