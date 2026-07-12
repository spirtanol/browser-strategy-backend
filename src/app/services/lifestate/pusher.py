from typing import Callable

from app.core.db import Redis


class LifeStatePusher:
    def __init__(self, redis_factory: Callable[[], Redis], ttl: int):
        self._redis_factory = redis_factory
        self._ttl = ttl

    async def keep_alive_ship(self, id: int):
        redis = self._redis_factory()
        if await redis.exists(f'a_ship:{id}') == 0:
            await redis.publish('alive', f'ship:{id}')
        await redis.set(f'a_ship:{id}', 1, ex=self._ttl)

    async def put_ship_to_sleep(self, id: int):
        redis = self._redis_factory()
        await redis.delete(f'a_ship:{id}')

    async def keep_alive_user(self, id: int):
        redis = self._redis_factory()
        if await redis.exists(f'a_user:{id}') == 0:
            await redis.publish('alive', f'user:{id}')
        await redis.set(f'a_user:{id}', 1, ex=self._ttl)

    async def put_user_to_sleep(self, id: int):
        redis = self._redis_factory()
        await redis.delete(f'a_user:{id}')

    async def keep_alive_fleet(self, id: int):
        redis = self._redis_factory()
        if await redis.exists(f'a_fleet:{id}'):
            await redis.publish('alive', f'fleet:{id}')
        await redis.set(f'a_fleet:{id}', 1, ex=self._ttl)

    async def put_fleet_to_sleep(self, id: int):
        redis = self._redis_factory()
        await redis.delete(f'a_fleet:{id}')