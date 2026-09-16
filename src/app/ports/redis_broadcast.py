from collections.abc import Callable, Sequence

from redis.asyncio import Redis

from app.ports.broadcast import ChannelMessage


class RedisBroadcast:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory

    async def publish(self, channel: str, payload: str) -> None:
        redis = self._redis_factory()
        await redis.publish(channel, payload)

    async def publish_many(self, items: Sequence[ChannelMessage]) -> None:
        if not items:
            return

        redis = self._redis_factory()
        async with redis.pipeline() as pipe:
            for item in items:
                pipe.publish(item.channel, item.payload)
            await pipe.execute()
