from logging import Logger
from typing import Optional, Callable
import asyncio

from redis.asyncio import Redis

from app.services.lifestate.pusher import LifeStatePusher
from app.schemas.fleet import FleetStateOut


_alive_fleets: dict[int, int] = {}

class ClientFleetService:
    def __init__(
        self, 
        redis_factory: Callable[[], Redis],
        life_state_pusher: LifeStatePusher
    ):
        self._redis_factory = redis_factory
        self._state_pusher = life_state_pusher

    async def find(self, id: int) -> Optional[FleetStateOut]:
        redis = self._redis_factory()
        fleet_raw = await redis.get(f'c_fleet:{id}')
        return FleetStateOut.model_validate_json(fleet_raw) if fleet_raw else None

    async def subscribe_to_updates(self, id: int, logger: Logger) -> str:
        redis = self._redis_factory()
        subscriber = redis.pubsub()
        channel_name = f'fleet:{id}'
        if id in _alive_fleets:
            _alive_fleets[id] += 1
        else:
            _alive_fleets[id] = 1
        await subscriber.subscribe(channel_name)
        await self._state_pusher.keep_alive_fleet(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    yield message['data']

                    now = asyncio.get_event_loop().time()
                    if now - last_keep_alive > 60:
                        await self._state_pusher.keep_alive_fleet(id)
                        last_keep_alive = now
        except Exception as e:
            logger.exception('Ошибка при получении данных флота из ядра')
        finally:
            _alive_fleets[id] -= 1
            if _alive_fleets[id] <= 0:
                await self._state_pusher.put_fleet_to_sleep(id)
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()