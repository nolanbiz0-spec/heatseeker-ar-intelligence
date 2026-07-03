from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Float, Boolean, Text, JSON
from datetime import datetime
import redis.asyncio as redis
from .config import settings


# Database Models Base
class Base(DeclarativeBase):
    pass


# Async Database Engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=30
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


# Redis Connection
redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_db() -> AsyncSession:
    """Database dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """Redis dependency"""
    return redis_client


# Database initialization
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
    await redis_client.close()