from functools import cached_property
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import enum

from app.core.config import AppSettings, get_config
from app.core.db import get_engine, get_session_maker, AsyncSession, get_redis, Redis
from app.services.ship import ShipService, ShipRepository
from app.services.command_handler import CommandHandlerService
from app.services.command_dispatcher import CommandDispatherService
from app.services.client_ship import ClientShipService
from app.services.lifestate.pusher import LifeStatePusher
from app.services.lifestate.registry import LifeStateRegistry


class Container:
    def __init__(self, config: AppSettings):
        self.config = config
        self._session = None

    @cached_property
    def ship_service(self) -> ShipService:
        return ShipService(
            repository=ShipRepository(self.get_session),
            redis_factory=self.get_redis,
            life_state_registry=self.life_state_registry
        )

    @cached_property
    def client_ship_service(self) -> ClientShipService:
        return ClientShipService(
            redis_factory=self.get_redis, 
            life_state_pusher=self.life_state_pusher,
            command_dispatcher=self.command_dispatcher_service
        )

    @cached_property
    def command_handler_service(self) -> CommandHandlerService:
        return CommandHandlerService(
            ship_service=self.ship_service,
            life_state_registry=self.life_state_registry
        )

    @cached_property
    def command_dispatcher_service(self) -> CommandDispatherService:
        return CommandDispatherService(
            redis_factory=self.get_redis
        )
    
    @cached_property
    def life_state_pusher(self) -> LifeStatePusher:
        return LifeStatePusher(
            redis_factory=self.get_redis,
            ttl=self.config.alive_objects_duration
        )

    @cached_property
    def life_state_registry(self) -> LifeStateRegistry:
        return LifeStateRegistry(
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

async def get_container() -> Container:
    container = Container(
        config=get_config()
    )
    yield container

    await container.end()

get_context_container = asynccontextmanager(get_container)