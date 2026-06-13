from typing import Callable, Type

from pydantic import BaseModel

from .resolvers.base import ResolveResult, ResolverContext
from app.entities.user import UserEntity
from app.entities.world import World
from .registry import COMMAND_CONFIG


class NotFoundCommandError(Exception):
    pass

def get_resolver(com_name: str) -> tuple[Callable[[ResolverContext, UserEntity, BaseModel], ResolveResult], Type[BaseModel]]:
    if com_name not in COMMAND_CONFIG:
        raise NotFoundCommandError(com_name)

    command_item = COMMAND_CONFIG.get(com_name)
    return command_item['resolver'], command_item['dto']

def get_command(com_name: str) -> tuple[Callable[[World, BaseModel], None], Type[BaseModel]]:
    if com_name not in COMMAND_CONFIG:
        raise NotFoundCommandError(com_name)

    command_item = COMMAND_CONFIG.get(com_name)
    return command_item['handler'], command_item['dto']
    