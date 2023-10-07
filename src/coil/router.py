from fastapi import APIRouter, Depends

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker


router = APIRouter(
    prefix='/coil',
    tags=["Coil"]
)
