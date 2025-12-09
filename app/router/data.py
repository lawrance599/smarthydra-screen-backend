from fastapi import APIRouter, Depends, Query, HTTPException, Form, Path
from typing import Annotated
from sqlmodel import select
from app.deps.user import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.engine import get_session
from app.database.schema import Station, WaterLevelData, RainfallData
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(
    prefix="/data",
    tags=["data"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/{station_id}/water-level")
async def read_water_level_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    station_id: Annotated[int, Path()],
    limit: Annotated[int, Query(ge=1, le=1000)],
):
    """
    获取指定站点的指定时间段内的水位数据
    """
    query = (
        select(WaterLevelData)
        .where(WaterLevelData.station_id == station_id)
        .order_by(WaterLevelData.measure_at.desc())
        .limit(limit)
    )
    water_level_data = (await session.execute(query)).scalars().all()
    return [item.model_dump() for item in water_level_data]


class DataInsert(BaseModel):
    measure_at: datetime | None = None
    value: float


@router.post("/{station_id}/water-level")
async def create_water_level_data(
    station_id: Annotated[int, Path()],
    form: Annotated[DataInsert, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    创建指定站点的水位数据
    """
    station = (
        (await session.execute(select(Station).where(Station.id == station_id))).scalars().first()
    )
    if not station:
        raise HTTPException(404, "站点不存在")
    if not form.measure_at:
        form.measure_at = datetime.now(timezone.utc)
    water_level_data = WaterLevelData(
        station_id=station_id,
        measure_at=form.measure_at,
        value=form.value,
    )
    session.add(water_level_data)
    await session.commit()
    return water_level_data.model_dump()


@router.delete("{station_id}/water-level/{id}")
async def delete_water_level_data(
    station_id: Annotated[int, Path()],
    id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    删除指定站点的水位数据
    """
    water_level_data = (
        (
            await session.execute(
                select(WaterLevelData)
                .where(WaterLevelData.id == id)
                .where(WaterLevelData.station_id == station_id)
            )
        )
        .scalars()
        .first()
    )
    if not water_level_data:
        raise HTTPException(404, "数据不存在")
    return water_level_data.model_dump()


@router.get("/rainfall")
async def read_rainfall_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    station_id: int,
    limit: Annotated[int, Query(ge=1, le=1000)],
):
    """
    获取指定站点的指定时间段内的雨量数据
    """
    query = (
        select(RainfallData)
        .where(RainfallData.station_id == station_id)
        .order_by(RainfallData.measure_at.desc())
        .limit(limit)
    )

    rainfall_data = (await session.execute(query)).scalars().all()
    return [item.model_dump() for item in rainfall_data]


@router.post("/{station_id}/rainfall")
async def create_rainfall_data(
    station_id: Annotated[int, Path()],
    form: Annotated[DataInsert, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    创建指定站点的雨量数据
    """
    station = (
        (await session.execute(select(Station).where(Station.id == station_id))).scalars().first()
    )
    if not station:
        raise HTTPException(404, "站点不存在")
    if not form.measure_at:
        form.measure_at = datetime.now(timezone.utc)

    rainfall_data = RainfallData(
        station_id=station_id,
        measure_at=form.measure_at,
        value=form.value,
    )
    session.add(rainfall_data)
    await session.commit()
    return rainfall_data.model_dump()


@router.delete("{station_id}/rainfall/{id}")
async def delete_rainfall_data(
    station_id: Annotated[int, Path()],
    id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    删除指定站点的雨量数据
    """
    rainfall_data = (
        (
            await session.execute(
                select(RainfallData)
                .where(RainfallData.id == id)
                .where(RainfallData.station_id == station_id)
            )
        )
        .scalars()
        .first()
    )
    if not rainfall_data:
        raise HTTPException(404, "数据不存在")
    return rainfall_data.model_dump()
