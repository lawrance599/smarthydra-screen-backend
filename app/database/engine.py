from sqlmodel import create_engine, SQLModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.settings import Settings
from typing import AsyncGenerator

# 获取配置
settings = Settings.new()

# 将同步数据库URL转换为异步URL
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# 创建异步数据库引擎
async_engine = create_async_engine(
    async_database_url,
    echo=settings.logging_level == "DEBUG",  # 开发环境下打印SQL语句
    pool_size=20,  
    max_overflow=30,  
    pool_pre_ping=True,  
    pool_recycle=3600,  
    connect_args={
        "command_timeout": 60,  # 命令超时时间
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



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话的依赖注入函数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """异步初始化数据库，创建所有表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

