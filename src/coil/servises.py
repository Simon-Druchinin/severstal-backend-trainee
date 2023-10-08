from sqlalchemy import exists, select, and_, func
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from src.coil.models import Coil
from src.coil.schemas import DateRangeSchema


async def coil_exists(id: int, session: AsyncSession) -> bool:
    query = select(exists().where(Coil.id == id))
    result = await session.execute(query)
    
    return result.scalar()

async def is_coil_deleted(id: int, session: AsyncSession) -> bool:
    query = select(exists().where(and_(Coil.id == id, Coil.deleted_at.isnot(None))))
    result = await session.execute(query)
    
    return result.scalar()

def get_date_range_filter(model: Coil, date_range: DateRangeSchema):
    return and_(model.created_at >= date_range.from_date, model.created_at <= date_range.to_date)

async def get_coil_base_stats(date_range: DateRangeSchema, session: AsyncSession) -> dict:
    date_filter = and_(Coil.created_at >= date_range.from_date, Coil.created_at <= date_range.to_date)

    query = select(
                func.count().label("amount"),
                func.sum(Coil.length).label("total_length"),
                func.sum(Coil.weight).label("total_weight"),
                func.max(Coil.length).label("max_length"),
                func.min(Coil.length).label("min_length"),
                func.max(Coil.weight).label("max_weight"),
                func.min(Coil.weight).label("min_weight"),
    ).select_from(Coil).where(get_date_range_filter(Coil, date_range))

    result = await session.execute(query)
    coil_stats = dict(zip(result.keys(), result.first()))

    query = select(func.count()).select_from(Coil).where(and_(date_filter, Coil.deleted_at.isnot(None)))
    deleted_amount = (await session.execute(query)).scalar()

    coil_stats['deleted_amount'] = deleted_amount

    return coil_stats

async def get_coil_date_stats(date_range: DateRangeSchema, session: AsyncSession) -> dict:
    coil1 = aliased(Coil, name='coil1')
    coil2 = aliased(Coil, name='coil2')
    query = select(
        func.max(coil2.created_at - coil1.created_at).label("creation_max_time_gap"),
        func.min(coil2.created_at - coil1.created_at).label("creation_min_time_gap"),
        func.max(coil2.deleted_at - coil1.deleted_at).label("deletion_max_time_gap"),
        func.min(coil2.deleted_at - coil1.deleted_at).label("deletion_min_time_gap"),
    ).select_from(coil1, coil2).where(
        and_(
            get_date_range_filter(coil1, date_range),
            get_date_range_filter(coil2, date_range),
            coil1.id+1 == coil2.id
        )
    )
    result = await session.execute(query)

    date_stats = dict(zip(result.keys(), result.first()))

    return date_stats
