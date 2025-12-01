from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.exc import SQLAlchemyError
from app.settings import load_settings
from typing import AsyncGenerator

_async_engine: AsyncEngine | None
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        raise RuntimeError("init_db() must be called before get_session()")
    async with _AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    settings = load_settings()
    
    global _async_engine, _AsyncSessionLocal
    _async_engine = create_async_engine(
        settings.database_url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_recycle=settings.database.pool_recycle,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
    )
    
    _AsyncSessionLocal = async_sessionmaker(
        _async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with _async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
