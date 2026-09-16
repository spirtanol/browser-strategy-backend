from typing import AsyncContextManager, Callable

from app.ports.broadcast import Broadcast
from app.schemas.commands import GameCommand
from app.entities.player import PlayerEntity
from .commands.factory import get_resolver, ResolverContext


class CommandDispatcherService:
    def __init__(
        self, 
        broadcast: Broadcast,
        resolver_context: ResolverContext,
        transaction: Callable[[], AsyncContextManager[None]],
        channel_name: str = 'commands'
    ):
        self._broadcast = broadcast
        self.channel_name = channel_name
        self._resolver_context = resolver_context
        self._transaction = transaction
        
    async def dispatch(self, command: GameCommand, player: PlayerEntity):
        async with self._transaction():
            resolver, dto_class = get_resolver(command.action)
            dto = dto_class.model_validate({'id': command.id, **command.params})
            await resolver(self._resolver_context, player, dto)
            
            await self._broadcast.publish(
                self.channel_name,
                command.model_dump_json()
            )
