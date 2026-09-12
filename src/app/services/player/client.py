import asyncio
from typing import AsyncContextManager, AsyncGenerator, Callable, Optional
from logging import Logger

from app.repositories.player import PlayerRepository
from app.entities.player import PlayerEntity
from app.core.db import Redis
from app.services.lifestate.pusher import LifeStatePusher


_alive_players: dict[int, int] = {}

class ClientPlayerService:
    def __init__(
        self,
        player_repository: PlayerRepository,
        redis_factory: Callable[[], Redis],
        life_state_pusher: LifeStatePusher,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self._player_repo = player_repository
        self._redis_factory = redis_factory
        self._state_pusher = life_state_pusher
        self._transaction = transaction

    async def find(self, id: int) -> Optional[PlayerEntity]:
        async with self._transaction():
            return await self._player_repo.find(id)

    async def subscribe_to_updates(self, id: int, logger: Logger) -> AsyncGenerator[str, None]:
        redis = self._redis_factory()
        subscriber = redis.pubsub()
        channel_name = f'player:{id}'
        if id in _alive_players:
            _alive_players[id] += 1
        else:
            _alive_players[id] = 1
        await subscriber.subscribe(channel_name)
        await self._state_pusher.keep_alive_player(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    yield message['data']

                    now = asyncio.get_event_loop().time()
                    if now - last_keep_alive > 60:
                        await self._state_pusher.keep_alive_player(id)
                        last_keep_alive = now
        except Exception as e:
            logger.exception('Ошибка при получении данных игрока из ядра')
        finally:
            _alive_players[id] -= 1
            if _alive_players[id] == 0:
                await self._state_pusher.put_player_to_sleep(id)
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()
