import asyncio
from typing import Callable, Optional
from logging import Logger

from app.repositories.user import UserRepository, UserEntity
from app.core.db import Redis
from app.services.lifestate.pusher import LifeStatePusher


_alive_users: dict[int, int] = {}

class ClientUserService:
    def __init__(
        self, 
        user_repository: UserRepository,
        redis_factory: Callable[[], Redis],
        life_state_pusher: LifeStatePusher
    ):
        self._user_repo = user_repository
        self._redis_factory = redis_factory
        self._state_pusher = life_state_pusher

    async def find(self, id: int) -> Optional[UserEntity]:
        return await self._user_repo.find(id)

    async def subscribe_to_updates(self, id: int, logger: Logger) -> str:
        redis = self._redis_factory()
        subscriber = redis.pubsub()
        channel_name = f'user:{id}'
        if id in _alive_users:
            _alive_users[id] += 1
        else:
            _alive_users[id] = 1
        await subscriber.subscribe(channel_name)
        await self._state_pusher.keep_alive_user(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    yield message['data']

                    now = asyncio.get_event_loop().time()
                    if now - last_keep_alive > 60:
                        await self._state_pusher.keep_alive_user(id)
                        last_keep_alive = now
        except Exception as e:
            logger.exception('Ошибка при получении данных пользователя из ядра')
        finally:
            _alive_users[id] -= 1
            if _alive_users[id] == 0:
                await self._state_pusher.put_user_to_sleep(id)
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()