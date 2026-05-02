from typing import Callable, override

from .ship import ShipRepository
from .ship_sql import ShipSQLRepository, ShipEntity, Optional
from .ship_redis import ShipRedisRepository


class ShipCompositeRepository(ShipRepository):
    def __init__(self, sql_repository: ShipSQLRepository, redis_repository: ShipRedisRepository):
        self._sql_repository = sql_repository
        self._redis_repository = redis_repository
        self.is_loaded = False
        self._identity_map = None

    async def find(self, id: int) -> Optional[ShipEntity]:
        if not self.is_loaded:
            await self.get_all()
        return self._identity_map.get(id, None)
        
    @override
    async def get_all(self) -> list[ShipEntity]:
        if not self.is_loaded:
            entities = await self._sql_repository.get_all()
            self._identity_map = {ent.id: ent for ent in entities}
            self.is_loaded = True
        return self._identity_map.values()

    @override
    async def save(self, entities: list[ShipEntity]):
        await self._sql_repository.save(entities)
        await self._redis_repository.save(entities)

        if self.is_loaded:
            for entity in entities:
                if entity.id not in self._identity_map:
                    self._identity_map[entity.id] = entity

    @override
    async def is_empty(self) -> bool:
        return await self._sql_repository.is_empty()

    async def flush(self, entities: list[ShipEntity]):
        await self._redis_repository.flush(entities)