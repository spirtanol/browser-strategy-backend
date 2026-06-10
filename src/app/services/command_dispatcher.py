from typing import Callable
import inspect

from redis.asyncio import Redis

from app.schemas.commands import GameCommand
from app.entities.user import UserEntity
from .commands.factory import get_resolver, ResolverContext


class CommandDispatcherService:
    def __init__(
        self, 
        redis_factory: Callable[[], Redis],
        resolver_context: ResolverContext,
        channel_name: str = 'commands',
    ):
        self.redis_factory = redis_factory
        self.channel_name = channel_name
        self._resolver_context = resolver_context

    async def dispatch(self, command: GameCommand, user: UserEntity):
        resolver, dto_class = get_resolver(command.action)
        dto = dto_class.model_validate(command.params)
        result = resolver(self._resolver_context, user, dto)
        
        if inspect.isawaitable(result):
            result = await result
        
        if result.success:
            redis_client = self.redis_factory()

            await redis_client.publish(
                self.channel_name,
                command.model_dump_json()
            )
