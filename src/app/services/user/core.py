from typing import Optional, Callable
import json

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.user import UserRepository
from app.entities.user import UserEntity
from app.mappers.user import UserMapper
from app.core.db import Redis
from app.services.lifestate.registry import LifeStateRegistry


class CoreUserService:
    def __init__(
        self, 
        user_repo: UserRepository, 
        user_mapper: UserMapper,
        redis_factory: Callable[[], Redis],
        life_state_registry: LifeStateRegistry
    ):
        self._user_repo = user_repo
        self._identity_map: dict[int, UserEntity] = None
        self._user_mapper = user_mapper
        self._redis_factory = redis_factory
        self._life_state_registry = life_state_registry

    async def load(self):
        entities = await self._user_repo.get_all()
        self._identity_map = {ent.id: ent for ent in entities}

    def get_all(self) -> list[UserEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self._user_repo.save(self._identity_map.values())

    async def flush(self):
        if self._identity_map is None:
            return

        redis = self._redis_factory()

        for entity in self.get_all():
            if self._life_state_registry.is_alive_user(entity.id):
                payload = json.dumps(self._user_mapper.to_dict(entity))
                await redis.publish(f'user:{entity.id}', payload)
    
    def find(self, id: int) -> Optional[UserEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreUserService')
        return self._identity_map.get(id, None)