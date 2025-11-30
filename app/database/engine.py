from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.settings import load_settings
from typing import AsyncGenerator

# 获取配置
settings = load_settings()

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.database_url,
    pool_size=20,  
    max_overflow=30,  
    pool_pre_ping=True,  
    pool_recycle=3600,  
    connect_args={
        "command_timeout": 60,  
        "server_settings": {"application_name": "smarthydra_screen_backend", "timezone": "UTC"},
    },
)


# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)



async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError :
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

