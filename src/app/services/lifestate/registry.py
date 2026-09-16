from app.ports.cache import Cache


class LifeStateRegistry:
    def __init__(self, cache: Cache):
        self._cache = cache
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

    def alive_handler(self, payload: str):
        ename, id = payload.split(':')
        id = int(id)
        match ename:
            case 'ship':
                self.add_ship(id)
            case 'player':
                self.add_player(id)
            case 'fleet':
                self.add_fleet(id)

    async def check_active(self):
        current_ids = list(self._fleet_ids)
        results = await self._cache.exists_many([f'a_fleet:{oid}' for oid in current_ids])
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._fleet_ids.remove(oid)

        current_ids = list(self._ship_ids)
        results = await self._cache.exists_many([f'a_ship:{oid}' for oid in current_ids])
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._ship_ids.remove(oid)

        current_ids = list(self._player_ids)
        results = await self._cache.exists_many([f'a_player:{oid}' for oid in current_ids])
        for oid, exists in zip(current_ids, results):
            if not exists:
                self._player_ids.remove(oid)
