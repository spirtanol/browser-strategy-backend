from typing import Optional, Callable
import asyncio
import json

from redis.asyncio import Redis

from app.entities.ship import ShipEntity
from app.repositories.ship import ShipRepository
from app.services.lifestate.pusher import LifeStatePusher
from app.mappers.ship import ShipMapper


_alive_ships: dict[int, int] = {}

class ClientShipService:
    def __init__(
        self, 
        ship_repository: ShipRepository,
        redis_factory: Callable[[], Redis],
        life_state_pusher: LifeStatePusher,
        ship_mapper: ShipMapper
    ):
        self._ship_repo = ship_repository
        self._redis_factory = redis_factory
        self._state_pusher = life_state_pusher
        self._ship_mapper = ship_mapper

    async def find(self, id: int) -> Optional[ShipEntity]:
        return await self._ship_repo.find(id)

    async def subscribe_to_updates(self, id: int) -> ShipEntity:
        redis = self._redis_factory()
        subscriber = redis.pubsub()
        channel_name = f'ship:{id}'
        if id in _alive_ships:
            _alive_ships[id] += 1
        else:
            _alive_ships[id] = 1
        await subscriber.subscribe(channel_name)
        await self._state_pusher.keep_alive_ship(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    raw_data = json.loads(message['data'])
                    
                    yield self._ship_mapper.from_dict(raw_data)

                    now = asyncio.get_event_loop().time()
                    if now - last_keep_alive > 60:
                        await self._state_pusher.keep_alive_ship(id)
                        last_keep_alive = now
        except Exception as e:
            print(str(e))
        finally:
            _alive_ships[id] -= 1
            if _alive_ships[id] == 0:
                await self._state_pusher.put_ship_to_sleep(id)
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()