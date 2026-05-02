from typing import Callable, override
import json

from redis.asyncio import Redis

from .ship import ShipRepository, ShipEntity, Optional


class ShipRedisRepository(ShipRepository):
    def __init__(self, redis_factory: Callable[[], Redis], ttl: int = 60):
        self._redis_factory = redis_factory
        self._ttl = ttl

    @override
    async def get_all(self) -> list[ShipEntity]:
        redis = self._redis_factory()
        ships = []

        keys = [key async for key in redis.scan_iter("ship:*")]

        if not keys:
            return [] 

        for raw_data in await redis.mget(keys):
            if raw_data:
                ship_data = json.loads(raw_data)
                ship = ShipEntity.from_dict(ship_data)
                ships.append(ship)

        return ships

    async def find(self, id: int) -> Optional[ShipEntity]:
        redis = self._redis_factory()

        raw_data = await redis.get(f'ship:{id}')

        if raw_data:
            ship_data = json.loads(raw_data)
            return ShipEntity.from_dict(ship_data)
        return None

    @override
    async def is_empty(self) -> bool:
        redis = self._redis_factory()
        async for _ in redis.scan_iter("ship:*", count=1):
            return True
        return False

    async def flush(self, entities: list[ShipEntity]):
        redis = self._redis_factory()

        for entity in entities:
            payload = json.dumps(entity.to_dict())
            await redis.set(f'ship:{entity.id}', payload, ex=self._ttl)