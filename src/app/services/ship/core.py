from typing import Optional, Callable
import json

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.ship import ShipRepository, ShipEntity
from app.core.db import Redis
from app.services.lifestate.registry import LifeStateRegistry
from app.mappers.ship import ShipMapper


class CoreShipService:
    def __init__(
        self, 
        repository: ShipRepository,
        life_state_registry: LifeStateRegistry,
        redis_factory: Callable[[], Redis],
        ship_mapper: ShipMapper
    ):
        self.repository = repository
        self._identity_map: dict[int, ShipEntity] = None
        self._redis_factory = redis_factory
        self._life_state_registry = life_state_registry
        self._ship_mapper = ship_mapper

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
                payload = json.dumps(self._ship_mapper.to_dict(entity))
                await redis.publish(f'ship:{entity.id}', payload)
    
    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[ShipEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreShipService')
            
        return self._identity_map.get(id, None)