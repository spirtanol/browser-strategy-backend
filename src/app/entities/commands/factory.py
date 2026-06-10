from typing import Type

from .base import BaseCommand


_MAP: dict[str, Type[BaseCommand]] = {}

class NotFoundCommandError(Exception):
    pass

def register_command():
    def wrapper(cls):
        _MAP[cls.name] = cls
        return cls
    return wrapper

def load(command_name: str, data: dict[str, any]) -> BaseCommand:
    command_class = _MAP.get(command_name, None)

    if not command_class:
        raise NotFoundCommandError()

    command = command_class()
    command.from_dict(data)
    return command