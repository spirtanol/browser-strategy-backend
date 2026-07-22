from typing import Callable, Any, Type, Awaitable

from .handlers.base import UserCommand
from .resolvers.base import ResolverContext
from app.entities.user import UserEntity
from app.entities.world import World
from .registry import COMMAND_CONFIG


class NotFoundCommandError(Exception):
    pass

def get_resolver(com_name: str) -> tuple[Callable[[ResolverContext, UserEntity, UserCommand], Awaitable[Any]], Type[UserCommand]]:
    command_item = COMMAND_CONFIG.get(com_name, None)
    
    if command_item is None:
        raise NotFoundCommandError(com_name)
        
    return command_item['resolver'], command_item['dto']

def get_command(com_name: str) -> tuple[Callable[[World, UserCommand], Awaitable[Any] | None], Type[UserCommand]]:
    command_item = COMMAND_CONFIG.get(com_name, None)
    
    if command_item is None:
        raise NotFoundCommandError(com_name)

    return command_item['handler'], command_item['dto']
    