from collections.abc import Callable, Sequence

from redis.asyncio import Redis

from app.ports.cache import CacheSet


class RedisCache:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self._redis_factory = redis_factory

    async def get(self, key: str) -> str | None:
        redis = self._redis_factory()
        return await redis.get(key)

    async def set(self, key: str, value: str, *, ex: int | None = None, exat: int | None = None) -> None:
        redis = self._redis_factory()
        await redis.set(key, value, ex=ex, exat=exat)

    async def delete(self, key: str) -> None:
        redis = self._redis_factory()
        await redis.delete(key)

    async def exists(self, key: str) -> bool:
        redis = self._redis_factory()
        return bool(await redis.exists(key))

    async def set_many(self, items: Sequence[CacheSet]) -> None:
        if not items:
            return

        redis = self._redis_factory()
        async with redis.pipeline() as pipe:
            for item in items:
                pipe.set(item.key, item.value, ex=item.ex, exat=item.exat)
            await pipe.execute()

    async def delete_many(self, keys: Sequence[str]) -> None:
        if not keys:
            return

        redis = self._redis_factory()
        async with redis.pipeline() as pipe:
            for key in keys:
                pipe.delete(key)
            await pipe.execute()

    async def exists_many(self, keys: Sequence[str]) -> list[bool]:
        if not keys:
            return []

        redis = self._redis_factory()
        async with redis.pipeline() as pipe:
            for key in keys:
                pipe.exists(key)
            results = await pipe.execute()

        return [bool(exists) for exists in results]
