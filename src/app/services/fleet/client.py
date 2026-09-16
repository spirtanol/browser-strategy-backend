from logging import Logger
from typing import AsyncGenerator, Optional
import asyncio

from app.ports.cache import Cache
from app.ports.subscription import Subscription
from app.services.lifestate.pusher import LifeStatePusher
from app.schemas.fleet import FleetStateOut


_alive_fleets: dict[int, int] = {}

class ClientFleetService:
    def __init__(
        self, 
        cache: Cache,
        subscription: Subscription,
        life_state_pusher: LifeStatePusher
    ):
        self._cache = cache
        self._subscription = subscription
        self._state_pusher = life_state_pusher

    async def find(self, id: int) -> Optional[FleetStateOut]:
        fleet_raw = await self._cache.get(f'c_fleet:{id}')
        return FleetStateOut.model_validate_json(fleet_raw) if fleet_raw else None

    async def subscribe_to_updates(self, id: int, logger: Logger) -> AsyncGenerator[str, None]:
        channel_name = f'fleet:{id}'
        if id in _alive_fleets:
            _alive_fleets[id] += 1
        else:
            _alive_fleets[id] = 1
        await self._state_pusher.keep_alive_fleet(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for msg in self._subscription.listen(channel_name):
                yield msg.payload

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
