from typing import Optional, Callable
import json
import asyncio

from redis.asyncio import Redis

from app.entities.ship import ShipEntity
from .lifestate.pusher import LifeStatePusher
from .command_dispatcher import CommandDispatherService, GameCommand


class ClientShipService:
    def __init__(
        self, 
        redis_factory: Callable[[], Redis], 
        life_state_pusher: LifeStatePusher,
        command_dispatcher: CommandDispatherService
    ):
        self._redis_factory = redis_factory
        self._life_state_pusher = life_state_pusher
        self._command_dispatcher = command_dispatcher

    async def find(self, id: int) -> Optional[ShipEntity]:
        redis = self._redis_factory()

        await self._life_state_pusher.keep_alive_ship(id)
        raw_data = await redis.get(f'ship:{id}')

        if raw_data is None:
            await self._command_dispatcher.dispatch(GameCommand(
                action='alive_ship',
                params={'ship_id': id}
            ))
            await asyncio.sleep(3)
            raw_data = await redis.get(f'ship:{id}')

        if raw_data:
            ship_data = json.loads(raw_data)
            return ShipEntity.from_dict(ship_data)
        return None