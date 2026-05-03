from typing import Callable

from app.core.db import Redis


class LifeStatePusher:
    def __init__(self, redis_factory: Callable[[], Redis], ttl: int):
        self._redis_factory = redis_factory
        self._ttl = ttl

    async def keep_alive_ship(self, id: int):
        redis = self._redis_factory()
        await redis.set(f'a_ship:{id}', 1, ex=self._ttl)