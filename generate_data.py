import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List
import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database.schema import City, Station, WaterLevelData, RainfallData

# 加载环境变量
load_dotenv()


# 创建数据库引擎和会话
async def create_db_session():
    """创建数据库会话"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=20,
        max_overflow=30,
    )

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    return engine, session_factory


# 中国主要城市列表
CHINESE_CITIES = [
    {"name": "北京", "code": "BJ", "lat": 39.9042, "lng": 116.4074},
    {"name": "上海", "code": "SH", "lat": 31.2304, "lng": 121.4737},
    {"name": "广州", "code": "GZ", "lat": 23.1291, "lng": 113.2644},
    {"name": "深圳", "code": "SZ", "lat": 22.5431, "lng": 114.0579},
    {"name": "杭州", "code": "HZ", "lat": 30.2741, "lng": 120.1551},
    {"name": "南京", "code": "NJ", "lat": 32.0603, "lng": 118.7969},
    {"name": "武汉", "code": "WH", "lat": 30.5928, "lng": 114.3055},
    {"name": "成都", "code": "CD", "lat": 30.5728, "lng": 104.0668},
    {"name": "重庆", "code": "CQ", "lat": 29.5630, "lng": 106.5516},
    {"name": "西安", "code": "XA", "lat": 34.3416, "lng": 108.9398},
    {"name": "天津", "code": "TJ", "lat": 39.0851, "lng": 117.1994},
    {"name": "苏州", "code": "SZ", "lat": 31.2989, "lng": 120.5853},
    {"name": "青岛", "code": "QD", "lat": 36.0671, "lng": 120.3826},
    {"name": "大连", "code": "DL", "lat": 38.9140, "lng": 121.6147},
    {"name": "厦门", "code": "XM", "lat": 24.4798, "lng": 118.0894},
    {"name": "长沙", "code": "CS", "lat": 28.2282, "lng": 112.9388},
    {"name": "郑州", "code": "ZZ", "lat": 34.7466, "lng": 113.6254},
    {"name": "济南", "code": "JN", "lat": 36.6512, "lng": 117.1201},
    {"name": "福州", "code": "FZ", "lat": 26.0745, "lng": 119.2965},
    {"name": "合肥", "code": "HF", "lat": 31.8206, "lng": 117.2272},
]


async def generate_cities() -> List[City]:
    """生成城市数据"""
    cities = []
    for city_data in CHINESE_CITIES:
        city = City(name=str(city_data["name"]), code=str(city_data["code"]))
        cities.append(city)
    return cities


async def generate_stations(cities: List[City]) -> List[Station]:
    """为每个城市生成测站数据"""
    stations = []

    for city in cities:
        # 每个城市生成1-3个测站
        station_count = random.randint(1, 3)

        for i in range(station_count):
            # 在城市坐标附近随机偏移
            city_info = next(c for c in CHINESE_CITIES if c["name"] == city.name)
            lat_offset = random.uniform(-0.5, 0.5)
            lng_offset = random.uniform(-0.5, 0.5)

            station = Station(
                name=f"{city.name}监测站{i + 1}",
                code=f"{city.code}_ST{i + 1:02d}",
                city_id=city.id if city.id is not None else 0,
                latitude=float(city_info["lat"]) + lat_offset,
                longitude=float(city_info["lng"]) + lng_offset,
                water_level_threshold=random.uniform(3.0, 5.0),
                rainfall_threshold=random.uniform(50.0, 100.0),
                is_active=True,
            )
            stations.append(station)

    return stations


def generate_water_level_data(station_id: int, days: int = 10) -> List[WaterLevelData]:
    """生成水位数据，平稳但有波动"""
    water_levels = []
    base_level = random.uniform(1.5, 3.0)  # 基础水位

    # 生成从现在往前推days天的数据，每小时一个数据点
    now = datetime.now()
    for day in range(days):
        for hour in range(24):
            measure_time = now - timedelta(days=day, hours=23 - hour)

            # 生成平稳但有波动的水位数据
            # 使用正弦波 + 随机噪声来模拟自然波动
            time_factor = (day * 24 + hour) / 24.0
            wave = 0.2 * math.sin(time_factor * 0.5)  # 缓慢波动
            noise = random.uniform(-0.1, 0.1)  # 小幅随机噪声
            value = base_level + wave + noise

            # 确保水位值在合理范围内
            value = max(0.5, min(5.0, value))

            water_level = WaterLevelData(
                station_id=station_id, value=round(value, 2), measure_at=measure_time
            )
            water_levels.append(water_level)

    return water_levels


def generate_rainfall_data(station_id: int, days: int = 10) -> List[RainfallData]:
    """生成雨量数据，大部分为0，少部分降雨"""
    rainfall_data = []

    # 生成从现在往前推days天的数据，每小时一个数据点
    now = datetime.now()
    for day in range(days):
        for hour in range(24):
            measure_time = now - timedelta(days=day, hours=23 - hour)

            # 90%的概率无降雨，10%的概率有降雨
            if random.random() < 0.9:
                value = 0.0
            else:
                # 有降雨时，雨量在0.1-50mm之间
                value = random.uniform(0.1, 50.0)

            rainfall = RainfallData(
                station_id=station_id, value=round(value, 2), measure_at=measure_time
            )
            rainfall_data.append(rainfall)

    return rainfall_data


async def main():
    """主函数，生成所有虚拟数据"""
    print("开始生成虚拟数据...")

    try:
        # 创建数据库引擎和会话
        engine, session_factory = await create_db_session()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请检查数据库配置或确保数据库服务正在运行")
        print("将生成演示数据而不保存到数据库...")

        # 生成演示数据并打印到控制台
        await generate_demo_data()
        return

    async with session_factory() as session:
        # 生成城市数据
        print("生成城市数据...")
        cities = await generate_cities()
        for city in cities:
            session.add(city)
        await session.commit()

        # 刷新以获取ID
        for city in cities:
            await session.refresh(city)

        print(f"已生成 {len(cities)} 个城市")

        # 生成测站数据
        print("生成测站数据...")
        stations = await generate_stations(cities)
        for station in stations:
            session.add(station)
        await session.commit()

        # 刷新以获取ID
        for station in stations:
            await session.refresh(station)

        print(f"已生成 {len(stations)} 个测站")

        # 生成水位和雨量数据
        print("生成水位和雨量数据...")
        water_level_count = 0
        rainfall_count = 0

        for station in stations:
            # 确保station.id不为None
            if station.id is None:
                continue

            # 生成水位数据
            water_levels = generate_water_level_data(station.id)
            for wl in water_levels:
                session.add(wl)
            water_level_count += len(water_levels)

            # 生成雨量数据
            rainfall = generate_rainfall_data(station.id)
            for rf in rainfall:
                session.add(rf)
            rainfall_count += len(rainfall)

            # 每处理5个测站提交一次，避免内存问题
            if stations.index(station) % 5 == 4:
                await session.commit()

        # 最后一次提交
        await session.commit()

        print(f"已生成 {water_level_count} 条水位数据")
        print(f"已生成 {rainfall_count} 条雨量数据")

        print("虚拟数据生成完成！")


async def generate_demo_data():
    """生成演示数据并打印到控制台"""
    print("\n=== 演示数据生成 ===")

    # 生成城市数据
    cities = await generate_cities()
    print(f"\n生成了 {len(cities)} 个城市:")
    for city in cities:
        print(f"  - {city.name} ({city.code})")
        # 模拟设置ID
        city.id = cities.index(city) + 1

    # 生成测站数据
    stations = await generate_stations(cities)
    print(f"\n生成了 {len(stations)} 个测站:")
    for station in stations:
        print(f"  - {station.name} ({station.code})")
        # 模拟设置ID
        station.id = stations.index(station) + 1

    # 生成水位和雨量数据示例
    print(f"\n为每个测站生成10天的水位和雨量数据...")
    for i, station in enumerate(stations[:3]):  # 只显示前3个测站的数据示例
        station_id = station.id if station.id is not None else i + 1
        water_levels = generate_water_level_data(station_id)
        rainfall = generate_rainfall_data(station_id)

        print(f"\n测站: {station.name}")
        print(f"  水位数据示例 (前5条):")
        for wl in water_levels[:5]:
            print(f"    {wl.measure_at.strftime('%Y-%m-%d %H:%M')}: {wl.value}m")

        print(f"  雨量数据示例 (前5条):")
        for rf in rainfall[:5]:
            print(f"    {rf.measure_at.strftime('%Y-%m-%d %H:%M')}: {rf.value}mm")

    print(f"\n总共将生成:")
    print(f"  - {len(cities)} 个城市")
    print(f"  - {len(stations)} 个测站")
    print(f"  - {len(stations) * 10 * 24} 条水位数据 (每个测站10天，每小时一条)")
    print(f"  - {len(stations) * 10 * 24} 条雨量数据 (每个测站10天，每小时一条)")


if __name__ == "__main__":
    asyncio.run(main())
