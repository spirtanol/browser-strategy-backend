from functools import cached_property
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import enum
from contextvars import ContextVar

from app.core.config import AppSettings, get_config
from app.core.db import get_engine, get_session_maker, AsyncSession, get_redis, Redis
from app.services.command_handler import CommandHandlerService
from app.services.command_dispatcher import CommandDispatcherService
from app.services.ship.client import ClientShipService
from app.services.ship.core import CoreShipService, ShipRepository
from app.services.ship.action import ShipService
from app.services.platform.core import CorePlatformService, PlatformRepository
from app.services.platform.action import PlatformService
from app.services.platform.client import ClientPlatformService
from app.services.lifestate.pusher import LifeStatePusher
from app.services.lifestate.registry import LifeStateRegistry
from app.services.token import TokenService
from app.services.auth import AuthService
from app.mappers.ship import ShipMapper
from app.mappers.user import UserMapper
from app.mappers.platform import PlatformMapper
from app.services.user.action import UserService, UserRepository
from app.services.user.core import CoreUserService
from app.services.user.client import ClientUserService


class Container:
    def __init__(self, config: AppSettings):
        self.config = config
        self._session_var: ContextVar[AsyncSession | None] = ContextVar("session", default=None) 

    @cached_property
    def token_service(self) -> TokenService:
        return TokenService(
            redis_factory=self.get_redis,
            access_ttl=self.config.access_token_ttl,
            refresh_ttl=self.config.refresh_token_ttl,
            secret_key=self.config.secret_key,
            token_alg=self.config.token_alg
        )

    @cached_property
    def platform_mapper(self) -> PlatformMapper:
        return PlatformMapper()

    @cached_property
    def platform_repository(self) -> PlatformRepository:
        return PlatformRepository(
            mapper=self.platform_mapper,
            session_factory=self.get_session
        )

    @cached_property
    def core_platform_service(self) -> CorePlatformService:
        return CorePlatformService(
            platform_mapper=self.platform_mapper,
            platform_repo=self.platform_repository,
            redis_factory=self.get_redis
        )

    @cached_property
    def client_platform_service(self) -> ClientPlatformService:
        return ClientPlatformService(
            platform_repository=self.platform_repository
        )

    @cached_property
    def platform_service(self) -> PlatformService:
        return PlatformService(
            platform_repo=self.platform_repository
        )

    @cached_property
    def user_mapper(self) -> UserMapper:
        return UserMapper()

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(
            session_factory=self.get_session,
            mapper=self.user_mapper
        )

    @cached_property
    def auth_service(self) -> AuthService:
        return AuthService(
            user_repo=self.user_repository,
            token_service=self.token_service
        )

    @cached_property
    def core_user_service(self) -> CoreUserService:
        return CoreUserService(
            user_repo=self.user_repository,
            user_mapper=self.user_mapper,
            life_state_registry=self.life_state_registry,
            redis_factory=self.get_redis
        )

    @cached_property
    def client_user_service(self) -> ClientUserService:
        return ClientUserService(
            user_repository=self.user_repository,
            redis_factory=self.get_redis,
            life_state_pusher=self.life_state_pusher,
            user_mapper=self.user_mapper
        )

    @cached_property
    def user_service(self) -> UserService:
        return UserService(
            user_repo=self.user_repository,
            user_mapper=self.user_mapper
        )

    @cached_property
    def ship_mapper(self) -> ShipMapper:
        return ShipMapper()

    @cached_property
    def ship_repository(self) -> ShipRepository:
        return ShipRepository(
            session_factory=self.get_session,
            mapper=self.ship_mapper
        )

    @cached_property
    def ship_service(self) -> ShipService:
        return ShipService(
            ship_repo=self.ship_repository
        )

    @cached_property
    def core_ship_service(self) -> CoreShipService:
        return CoreShipService(
            repository=self.ship_repository,
            redis_factory=self.get_redis,
            life_state_registry=self.life_state_registry,
            ship_mapper=self.ship_mapper
        )

    @cached_property
    def client_ship_service(self) -> ClientShipService:
        return ClientShipService(
            ship_repository=self.ship_repository,
            redis_factory=self.get_redis,
            life_state_pusher=self.life_state_pusher,
            ship_mapper=self.ship_mapper
        )

    @cached_property
    def command_handler_service(self) -> CommandHandlerService:
        return CommandHandlerService()

    @cached_property
    def command_dispatcher_service(self) -> CommandDispatcherService:
        return CommandDispatcherService(
            redis_factory=self.get_redis,
            resolver_context=self
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
        session = self._session_var.get()
        if session is None:
            raise RuntimeError("Сессия не инициализирована. Вызовите метод внутри контекста `transaction()`")

        return session

    def get_redis(self) -> Redis:
        return get_redis(self.config.redis_url)

    @asynccontextmanager
    async def transaction(self):
        engine = get_engine(self.config.database_url, self.config.debug)
        session_maker = get_session_maker(engine)
        session = session_maker()
        token = self._session_var.set(session)
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
            self._session_var.reset(token)

async def get_container() -> Container:
    container = Container(
        config=get_config()
    )
    yield container

get_context_container = asynccontextmanager(get_container)