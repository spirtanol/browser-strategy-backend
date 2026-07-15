from typing import Optional, Callable

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.ship import ShipRepository, ShipEntity
from app.core.db import Redis
from app.services.lifestate.registry import LifeStateRegistry
from app.schemas.ship import ShipDetailInfoOut


class CoreShipService:
    def __init__(
        self, 
        repository: ShipRepository,
        life_state_registry: LifeStateRegistry,
        redis_factory: Callable[[], Redis]
    ):
        self.repository = repository
        self._identity_map: dict[int, ShipEntity] = None
        self._redis_factory = redis_factory
        self._life_state_registry = life_state_registry

    async def load(self):
        entities = await self.repository.get_all()
        self._identity_map = {ent.id: ent for ent in entities}

    def get_all(self) -> list[ShipEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self.repository.save(self._identity_map.values())

    async def flush(self):
        if self._identity_map is None:
            return

        redis = self._redis_factory()

        for entity in self.get_all():
            if self._life_state_registry.is_alive_ship(entity.id):
                dto = ShipDetailInfoOut.from_entity(entity)
                await redis.publish(f'ship:{entity.id}', dto.model_dump_json())
    
    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[ShipEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreShipService')
            
        return self._identity_map.get(id, None)