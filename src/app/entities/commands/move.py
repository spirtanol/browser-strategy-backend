from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseCommand
from .factory import register_command
from ..world import World
from .undocking import UndockingCommand
from app.defs.enums import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity


@register_command()
class MoveCommand(BaseCommand):
    name = 'move'

    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__()
        self.x = x
        self.y = y

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['xy'] = [self.x, self.y]
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.x, self.y = data.get('xy', [0.0, 0.0])

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished:
            return

        if ship.moving_state == MovingState.Docked:
            undocking = UndockingCommand()
            undocking.is_dependend = True
            ship.command_queue.add(undocking, True)
            return

        delta = ship.max_speed / 3600.0 * dt
        ship.moving_state = MovingState.Move
        if ship.pos.move_to(self.x, self.y, delta):
            self.finished = True
            ship.moving_state = MovingState.Idle

    def cancel(self, ship: ShipEntity):
        if ship.moving_state == MovingState.Move:
            ship.moving_state = MovingState.Idle