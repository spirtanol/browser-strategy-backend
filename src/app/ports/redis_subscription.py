from collections.abc import AsyncGenerator, Callable

from redis.asyncio import Redis

from app.ports.broadcast import ChannelMessage


class RedisSubscription:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory

    async def listen(self, *channels: str) -> AsyncGenerator[ChannelMessage, None]:
        if not channels:
            return

        redis = self._redis_factory()
        subscriber = redis.pubsub()
        await subscriber.subscribe(*channels)
        try:
            async for message in subscriber.listen():
                if message['type'] == 'message':
                    yield ChannelMessage(
                        channel=message['channel'],
                        payload=message['data'],
                    )
        finally:
            await subscriber.unsubscribe(*channels)
            await subscriber.aclose()
