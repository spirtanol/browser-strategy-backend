from typing import Callable

from app.core.db import Redis


class LifeStateRegistry:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory
        self._ship_ids = set()
        self._user_ids = set()

    def is_alive_ship(self, id: int) -> bool:
        return id in self._ship_ids

    def add_ship(self, id: int):
        self._ship_ids.add(id)

    async def check_active(self):
        redis = self._redis_factory()
        pipeline = redis.pipeline()
        current_ids = list(self._ship_ids)
        for oid in current_ids:
            pipeline.exists(f"a_ship:{oid}")

        results = await pipeline.execute()
            
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._ship_ids.remove(oid)

        current_ids = list(self._user_ids)
        for oid in current_ids:
            pipeline.exists(f"a_user:{oid}")

        results = await pipeline.execute()
            
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._user_ids.remove(oid)

    def is_alive_user(self, id: int) -> bool:
        return id in self._user_ids

    def add_user(self, id: int):
        self._user_ids.add(id)
