from logging import Logger
from typing import AsyncGenerator, Callable

from redis.asyncio import Redis


class ClientJournalService:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory

    async def subscribe_to_updates(self, user_id: int, logger: Logger) -> AsyncGenerator[str, None]:
        redis = self._redis_factory()
        subscriber = redis.pubsub()
        channel_name = f'journal:{user_id}'
        await subscriber.subscribe(channel_name)

        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    yield message['data']
        except Exception:
            logger.exception('Ошибка при получении журнала из ядра')
        finally:
            await subscriber.unsubscribe(channel_name)
            await subscriber.aclose()
