from __future__ import annotations
from typing import Optional, Type, TYPE_CHECKING, Any

from .base import BaseShipModule
import app.defs.modules as ModuleDefs


_MAP: dict[str, Type[BaseModule]] = {}

class NotFoundModuleError(Exception):
    pass

def register_module(def_name: str):
    def wrapper(cls):
        _MAP[def_name] = cls
        return cls
    return wrapper

def load(def_name: str, data: dict[str, Any]) -> BaseShipModule:
    module_def = ModuleDefs.MAP.get(def_name, None)
    module_class = _MAP.get(def_name, None)

    if module_def and module_class:
        return module_class.from_dict(module_def, data)

    raise NotFoundModuleError()

def create(def_name: str, id: int, /, **kwargs) -> BaseShipModule:
    module_def = ModuleDefs.MAP.get(def_name, None)
    module_class = _MAP.get(def_name, None)

    if module_def and module_class:
        return module_class(module_def, id, **kwargs)

    raise NotFoundModuleError()