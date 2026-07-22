from logging import Logger
from typing import AsyncGenerator, Optional, Callable
import asyncio
import json

from redis.asyncio import Redis

from app.entities.ship import ShipEntity
from app.services.lifestate.pusher import LifeStatePusher

_alive_ships: dict[int, int] = {}

class ClientShipService:
    def __init__(
        self, 
        redis_factory: Callable[[], Redis],
        life_state_pusher: LifeStatePusher
    ):
        self._redis_factory = redis_factory
        self._state_pusher = life_state_pusher

    async def subscribe_to_updates(self, id: int, logger: Logger) -> AsyncGenerator[str, None]:
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
                    yield message['data']

                    now = asyncio.get_event_loop().time()
                    if now - last_keep_alive > 60:
                        await self._state_pusher.keep_alive_ship(id)
                        last_keep_alive = now
        except Exception as e:
            logger.exception('Ошибка при получении данных корабля из ядра')
        finally:
            _alive_ships[id] -= 1
            if _alive_ships[id] == 0:
                await self._state_pusher.put_ship_to_sleep(id)
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()