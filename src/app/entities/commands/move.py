from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseCommand
from .factory import register_command
from ..world import World
from .undocking import UndockingCommand
from app.core.types import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity


@register_command()
class MoveCommand(BaseCommand):
    name = 'move'

    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__()
        self.x = x
        self.y = y
        self.undocking = None

    def update(self, ship: ShipEntity, dt: float, world: World):
        if ship.state == MovingState.Docked and self.undocking is None:
            self.undocking = UndockingCommand()

        if self.undocking:
            self.undocking.update(ship, dt, world)
            if self.undocking.finished:
                self.undocking = None
            else:
                return

        delta = ship.max_speed / 3600.0 * dt
        ship.state = MovingState.Move
        if ship.pos.move_to(self.x, self.y, delta):
            self.finished = True
            ship.state = MovingState.Idle

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['xy'] = [self.x, self.y]
        if self.undocking:
            data['undocking'] = self.undocking.to_dict()
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.x, self.y = data.get('xy', [0.0, 0.0])
        if 'undocking' in data:
            self.undocking = UndockingCommand()
            self.undocking.from_dict(data['undocking'])