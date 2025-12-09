from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlmodel import select
from app.deps.user import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.engine import get_session
from app.database.schema import WaterLevelData, RainfallData

router = APIRouter()


@router.get("/data/water-level")
async def read_water_level_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    station_id: int,
    limit: Annotated[int, Query(ge=1, le=1000)],
):
    """
    获取指定站点的指定时间段内的水位数据
    """
    query = select(WaterLevelData).limit(limit).where(WaterLevelData.station_id == station_id)
    water_level_data = (await session.execute(query)).scalars().all()
    return [water_level_data.model_dump() for water_level_data in water_level_data]


@router.get("/data/rainfall")
async def read_rainfall_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    station_id: int,
    limit: Annotated[int, Query(ge=1, le=1000)],
):
    """
    获取指定站点的指定时间段内的雨量数据
    """
    query = select(RainfallData).limit(limit).where(RainfallData.station_id == station_id)
    rainfall_data = (await session.execute(query)).scalars().all()
    return [rainfall_data.model_dump() for rainfall_data in rainfall_data]
