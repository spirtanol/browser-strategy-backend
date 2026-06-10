from typing import Optional, Type

from .base import BaseModule, Environment
import app.defs.modules as ModuleDefs


_MAP: dict[str, Type[BaseModule]] = {}

class NotFoundModuleError(Exception):
    pass

def register_module(def_name: str):
    def wrapper(cls):
        _MAP[def_name] = cls
        return cls
    return wrapper

def load(def_name: str, env: Environment, data: dict[str, any]) -> BaseModule:
    module_def = ModuleDefs.MAP.get(def_name, None)
    module_class = _MAP.get(def_name, None)

    if module_def and module_class:
        return module_class.from_dict(module_def, env, data)

    raise NotFoundModuleError()

def create(def_name: str, env: Environment, id: int, /, **kwargs) -> BaseModule:
    module_def = ModuleDefs.MAP.get(def_name, None)
    module_class = _MAP.get(def_name, None)

    if module_def and module_class:
        return module_class(module_def, env, id, **kwargs)

    raise NotFoundModuleError()