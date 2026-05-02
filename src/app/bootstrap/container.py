from functools import cached_property
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import enum

from app.core.config import AppSettings, get_config
from app.services.ship import ShipService, ShipRepository
from app.services.command_handler import CommandHandlerService
from app.services.command_dispatcher import ComandDispatherService
from app.core.db import get_engine, get_session_maker, AsyncSession, get_redis, Redis


class Mode:
    CORE = 1
    API = 2

class Container:
    def __init__(self, config: AppSettings, mode: Mode):
        self.config = config
        self._session = None
        self.mode = mode

    @cached_property
    def _ship_repository(self) -> ShipRepository:
        from app.repositories.ship_redis import ShipRedisRepository

        redis_repository = ShipRedisRepository(redis_factory=self.get_redis)

        if self.mode == Mode.CORE:
            from app.repositories.ship_composite import ShipCompositeRepository, ShipSQLRepository
            composite_repository = ShipCompositeRepository(
                sql_repository=ShipSQLRepository(self.get_session),
                redis_repository=redis_repository
            )
            return composite_repository

        # API
        return redis_repository

    @cached_property
    def ship_service(self) -> ShipService:
        return ShipService(
            repository=self._ship_repository
        )

    @cached_property
    def command_handler_service(self) -> CommandHandlerService:
        return CommandHandlerService(
            ship_service=self.ship_service
        )

    @cached_property
    def command_dispatcher_service(self) -> ComandDispatherService:
        return ComandDispatherService(
            redis_factory=self.get_redis
        )

    def get_session(self) -> AsyncSession:
        if self._session is None:
            engine = get_engine(self.config.database_url, self.config.debug)
            session_maker = get_session_maker(engine)
            self._session = session_maker()

        return self._session

    def get_redis(self) -> Redis:
        return get_redis(self.config.redis_url)

    @asynccontextmanager
    async def begin(self):
        try:
            yield
            await self.end()
        except Exception as e:
            await self.end(e)
            raise

    async def end(self, exception: Optional[Exception] = None):
        if not self._session:
            return

        try:
            if exception:
                await self._session.rollback()
            else:
                await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
        finally:
            await self._session.close()
            self._session = None

async def get_container(mode: Mode = Mode.CORE) -> Container:
    container = Container(
        config=get_config(),
        mode=mode
    )
    yield container

    await container.end()

get_context_container = asynccontextmanager(get_container)