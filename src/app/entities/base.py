from abc import ABC, abstractmethod
from typing import Optional

from app.defs.enums import ObjectType
from .world import World


class BaseEntity(ABC):
    def __init__(self):
        self.id: int = 0
        self._world: Optional[World] = None

    def update(self, dt: float):
        pass

class MapEntity(BaseEntity):
    def __init__(self):
        super().__init__()
        self._world: Optional[World] = None

    def bind_to_world(self, world: World):
        self._world = world

    @property
    def world(self) -> World:
        if self._world is None:
            raise RuntimeError(f"Попытка обращения к World вне core-процесса.")
        
        return self._world

    @abstractmethod
    def get_type(self) -> ObjectType: ...