from typing import Optional, Callable

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
        life_state_registry: LifeStateRegistry
    ):
        self._user_repo = user_repo
        self._identity_map: dict[int, UserEntity] = None
        self._life_state_registry = life_state_registry

    async def load(self):
        entities = await self._user_repo.get_all()
        self._identity_map = {ent.id: ent for ent in entities}

    def get_all(self) -> list[UserEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self._user_repo.save(self._identity_map.values())

    def flush(self, pipe: Pipeline):
        if self._identity_map is None:
            return

        for entity in self.get_all():
            if self._life_state_registry.is_alive_user(entity.id):
                dto = UserStateOut.from_entity(entity)
                pipe.publish(f'user:{entity.id}', dto.model_dump_json())
    
    def find(self, id: int) -> Optional[UserEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreUserService')
        return self._identity_map.get(id, None)