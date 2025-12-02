from fastapi import APIRouter, Depends, Form, HTTPException, Path
from app.deps.user import get_current_user
from app.database.engine import get_session
from app.database.schema import Station, City
from sqlmodel import select
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

router = APIRouter(
    prefix="/station",
    tags=["station"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/stations")
async def read_stations(session: Annotated[AsyncSession, Depends(get_session)]):
    """
    获取所有站点信息
    """
    try:
        statement = select(Station)
        stations = (await session.execute(statement)).all()
    except NoResultFound:
        raise HTTPException(404, "没有找到站点信息")
    except SQLAlchemyError:
        raise HTTPException(500, "服务器内部错误")
    return stations


class StationRead(BaseModel):
    id: int
    name: str
    code: str
    city: str
    longitude: float
    latitude: float


@router.get("/station/{station_id}", response_model=StationRead)
async def read_station(
    station_id: Annotated[int, Path()], session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    获取指定站点信息
    """
    statement = select(Station).where(Station.id == station_id)
    station = (await session.execute(statement)).scalars().first()
    if not station:
        raise HTTPException(404, "没有找到站点信息")
    statement = select(City).where(Station.id == station_id)
    city = (await session.execute(statement)).scalars().first()
    if not city:
        raise HTTPException(404, "没有找到城市信息")
    return StationRead(
        id=station.id, # type: ignore
        name=station.name,
        code=station.code,
        city=city.name,
        longitude=station.longitude,
        latitude=station.latitude,
    )

class StationCreate(BaseModel):
    name: str
    code: str
    city: str
    longitude: float
    latitude: float
    rainfall_threshold: float
    water_level_threshold: float

@router.post("/station", response_model=StationRead)
async def create_station(
    station: Annotated[StationCreate, Form()], session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    创建站点信息
    """
    statement = select(City).where(City.name == station.city)
    city = (await session.execute(statement)).scalars().first()
    if not city:
        raise HTTPException(404, "没有找到城市信息")
    statement = select(Station).where(Station.code == station.code)
    station_exist = (await session.execute(statement)).scalars().first()
    if station_exist:
        raise HTTPException(409, "站点已存在")
    new_station = Station(
        name=station.name,
        code=station.code,
        city_id=city.id, # type: ignore
        longitude=station.longitude,
        latitude=station.latitude,
        rainfall_threshold=station.rainfall_threshold,
        water_level_threshold=station.water_level_threshold,
    )
    session.add(station)
    await session.commit()
    await session.refresh(new_station)
    assert new_station.id
    return StationRead(
        id=new_station.id,
        name=station.name,
        code=station.code,
        city=city.name,
        longitude=station.longitude,
        latitude=station.latitude,
    )

