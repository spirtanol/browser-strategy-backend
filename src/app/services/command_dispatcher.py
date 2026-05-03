from typing import Callable

from redis.asyncio import Redis

from app.schemas.commands import GameCommand


class CommandDispatherService:
    def __init__(self, redis_factory: Callable[[], Redis], channel_name: str = 'commands'):
        self.redis_factory = redis_factory
        self.channel_name = channel_name

    async def dispatch(self, command: GameCommand):
        redis_client = self.redis_factory()

        await redis_client.publish(
            self.channel_name,
            command.model_dump_json()
        )
