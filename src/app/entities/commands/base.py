from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from .command_queue import CommandQueue
    from ..fleet import FleetEntity
    from ..world import World


class BaseCommand:
    name: str
    queue: CommandQueue

    def __init__(self):
        self.finished = False
        self.is_dependent = False

    def update(self, dt: float):
        pass

    def to_dict(self) -> dict[str, Any]:
        return {'_dep': self.is_dependent}

    def from_dict(self, data: dict[str, Any]):
        self.is_dependent = data.get('_dep', False)

    def cancel(self):
        pass

    @property
    def fleet(self) -> FleetEntity:
        return self.queue.fleet

    @property
    def world(self) -> World:
        return self.fleet.world