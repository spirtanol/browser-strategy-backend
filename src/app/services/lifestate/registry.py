from typing import Callable, Any

from app.core.db import Redis


class LifeStateRegistry:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory
        self._ship_ids = set()
        self._player_ids = set()
        self._fleet_ids = set()

    def add_ship(self, id: int):
        self._ship_ids.add(id)

    def is_alive_ship(self, id: int) -> bool:
        return id in self._ship_ids

    def add_fleet(self, id: int):
        self._fleet_ids.add(id)

    def is_alive_fleet(self, id: int) -> bool:
        return id in self._fleet_ids

    def remove_fleet(self, id: int):
        self._fleet_ids.remove(id)

    def add_player(self, id: int):
        self._player_ids.add(id)

    def is_alive_player(self, id: int) -> bool:
        return id in self._player_ids

    def alive_handler(self, message: dict[str, Any]):
        ename, id = message['data'].split(':')
        id = int(id)
        match ename:
            case 'ship':
                self.add_ship(id)
            case 'player':
                self.add_player(id)
            case 'fleet':
                self.add_fleet(id)

    async def check_active(self):
        redis = self._redis_factory()
        pipeline = redis.pipeline()

        # Проверяем флотилии
        current_ids = list(self._fleet_ids)
        for oid in current_ids:
            pipeline.exists(f"a_fleet:{oid}")

        results = await pipeline.execute()
            
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._fleet_ids.remove(oid)

        # Проверяем корабли
        current_ids = list(self._ship_ids)
        for oid in current_ids:
            pipeline.exists(f"a_ship:{oid}")

        results = await pipeline.execute()
            
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._ship_ids.remove(oid)

        # Проверяем игроков
        current_ids = list(self._player_ids)
        for oid in current_ids:
            pipeline.exists(f"a_player:{oid}")

        results = await pipeline.execute()
            
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._player_ids.remove(oid)
