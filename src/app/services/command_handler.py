import inspect

from app.schemas.commands import GameCommand
from app.entities.world import World
from .commands.factory import get_command


class CommandHandlerService:
    async def handle(self, command: GameCommand, world: World):
        command_handler, dto_class = get_command(command.action)
        handler_params = dto_class.model_validate(command.params)
        result = command_handler(world, handler_params)
        if inspect.isawaitable(result):
            await result
