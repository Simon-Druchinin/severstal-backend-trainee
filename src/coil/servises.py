from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.coil.models import Coil


async def coil_exists(id: int, session: AsyncSession) -> bool:
    query = select(exists().where(Coil.id == id))
    result = await session.execute(query)
    
    return result.scalar()
