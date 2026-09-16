from app.ports.broadcast import Broadcast
from app.ports.cache import Cache


class LifeStatePusher:
    def __init__(self, broadcast: Broadcast, cache: Cache, ttl: int):
        self._broadcast = broadcast
        self._cache = cache
        self._ttl = ttl

    async def keep_alive_ship(self, id: int):
        if not await self._cache.exists(f'a_ship:{id}'):
            await self._broadcast.publish('alive', f'ship:{id}')
        await self._cache.set(f'a_ship:{id}', '1', ex=self._ttl)

    async def put_ship_to_sleep(self, id: int):
        await self._cache.delete(f'a_ship:{id}')

    async def keep_alive_player(self, id: int):
        if not await self._cache.exists(f'a_player:{id}'):
            await self._broadcast.publish('alive', f'player:{id}')
        await self._cache.set(f'a_player:{id}', '1', ex=self._ttl)

    async def put_player_to_sleep(self, id: int):
        await self._cache.delete(f'a_player:{id}')

    async def keep_alive_fleet(self, id: int):
        if not await self._cache.exists(f'a_fleet:{id}'):
            await self._broadcast.publish('alive', f'fleet:{id}')
        await self._cache.set(f'a_fleet:{id}', '1', ex=self._ttl)

    async def put_fleet_to_sleep(self, id: int):
        await self._cache.delete(f'a_fleet:{id}')
