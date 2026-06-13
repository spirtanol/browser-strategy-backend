from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseCommand
from .factory import register_command
from ..world import World
from app.core.config import Consts
from app.core.types import MovingState, ObjectType

if TYPE_CHECKING:
    from ..ship import ShipEntity


@register_command()
class UndockingCommand(BaseCommand):
    name = 'undocking'

    def __init__(self):
        super().__init__()
        self.progress: float = 0.0

    def update(self, ship: ShipEntity, dt: float, world: World):
        if ship.state != MovingState.Docked and ship.state != MovingState.Maneuvering:
            self.finished = True
            return
        
        ship.state = MovingState.Maneuvering
        self.progress += dt

        if self.progress >= Consts.DockingTime * 0.5:
            ship.state = MovingState.Idle
            if ship.attached_to_type == ObjectType.Platform:
                platform = world.find_platform(ship.attached_to_id)
                ship.detach(platform)
            self.finished = True

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['progress'] = self.progress
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.progress = data.get('progress', 0.0)