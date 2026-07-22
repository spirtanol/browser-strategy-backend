from typing import AsyncContextManager, Optional, Callable

from redis.asyncio.client import Pipeline

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.user import UserRepository
from app.entities.user import UserEntity
from app.services.lifestate.registry import LifeStateRegistry
from app.schemas.user import UserStateOut


class CoreUserService:
    def __init__(
        self, 
        user_repo: UserRepository, 
        life_state_registry: LifeStateRegistry,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self._user_repo = user_repo
        self._identity_map: dict[int, UserEntity] = {}
        self._life_state_registry = life_state_registry
        self._transaction = transaction
        self._loaded: bool = False

    async def load(self):
        async with self._transaction():
            entities = await self._user_repo.get_all()
            self._identity_map = {ent.id: ent for ent in entities}
            self._loaded = True
    def get_all(self) -> list[UserEntity]:
        return list[UserEntity](self._identity_map.values())

    async def save(self):
        async with self._transaction():
            if self._identity_map:
                await self._user_repo.save(self.get_all())

    def flush(self, pipe: Pipeline):
        if not self._loaded:
            return

        for entity in self.get_all():
            if self._life_state_registry.is_alive_user(entity.id):
                dto = UserStateOut.from_entity(entity)
                pipe.publish(f'user:{entity.id}', dto.model_dump_json())
    
    def find(self, id: int) -> Optional[UserEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CoreUserService')
        return self._identity_map.get(id, None)