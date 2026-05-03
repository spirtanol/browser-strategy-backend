from typing import Optional, Callable
import json

from redis.asyncio import Redis

from app.repositories.ship import ShipRepository, ShipEntity
from .lifestate.registry import LifeStateRegistry


class ShipService:
    def __init__(
        self, 
        repository: ShipRepository,
        life_state_registry: LifeStateRegistry,
        redis_factory: Callable[[], Redis], 
        ttl: int = 60
    ):
        self.repository = repository
        self._identity_map: dict[int, ShipEntity] = None
        self._redis_factory = redis_factory
        self._ttl = ttl
        self._life_state_registry = life_state_registry

    async def get_all(self) -> list[ShipEntity]:
        if self._identity_map is None:
            entities = await self.repository.get_all()
            self._identity_map = {ent.id: ent for ent in entities}
        return self._identity_map.values()

    async def save(self):
        if self._identity_map is not None:
            await self.repository.save(self._identity_map.values())

    async def add(self, entity: ShipEntity):
        if self._identity_map is None:
            await self.get_all()
        await self.repository.save(entity)
        self._identity_map[entity.id] = entity

    async def flush(self):
        redis = self._redis_factory()

        entities = await self.get_all()

        for entity in entities:
            if self._life_state_registry.is_alive_ship(entity.id):
                payload = json.dumps(entity.to_dict())
                await redis.set(f'ship:{entity.id}', payload, ex=self._ttl)
    
    async def is_empty(self):
        return await self.repository.is_empty()

    async def find(self, id: int) -> Optional[ShipEntity]:
        if self._identity_map is None:
            await self.get_all()
        return self._identity_map.get(id, None)