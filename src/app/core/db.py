from typing import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import with_loader_criteria, Session
from redis.asyncio import Redis

from .disposer import reg_to_dispose


@lru_cache(maxsize=None)
def get_engine(db_url: str, debug: bool) -> AsyncEngine:
    engine = create_async_engine(
        db_url,
        echo=debug,
        pool_size=10,
        future=True,
        pool_pre_ping=True,
        pool_recycle=1800,
    )

    reg_to_dispose(engine.dispose)

    return engine

@lru_cache(maxsize=None)
def get_session_maker(engine: AsyncEngine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
    )   

async def get_session(session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
            
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

get_context_session = asynccontextmanager(get_session)

@lru_cache
def get_redis(redis_url: str) -> Redis:
    redis = Redis.from_url(redis_url, decode_responses=True)
    reg_to_dispose(redis.close)
    return redis