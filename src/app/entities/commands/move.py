from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .base import BaseCommand
from .factory import register_command
from .undocking import UndockingCommand
from app.defs.enums import MovingState


@register_command()
class MoveCommand(BaseCommand):
    name = 'move'

    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__()
        self.x = x
        self.y = y

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['xy'] = [self.x, self.y]
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.x, self.y = data.get('xy', [0.0, 0.0])

    def update(self, dt: float):
        if self.finished:
            return

        fleet = self.fleet

        if fleet.moving_state == MovingState.Docked:
            undocking = UndockingCommand()
            undocking.is_dependent = True
            self.queue.add(undocking, True)
            return

        delta = fleet.max_speed / 3600.0 * dt
        fleet.moving_state = MovingState.Move
        if fleet.pos.move_to(self.x, self.y, delta):
            self.finished = True
            fleet.moving_state = MovingState.Idle

    def cancel(self):
        if self.fleet.moving_state == MovingState.Move:
            self.fleet.moving_state = MovingState.Idle