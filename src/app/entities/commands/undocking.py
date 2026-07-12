from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .base import BaseCommand
from .factory import register_command
from ..world import World
import app.defs.consts as Consts
from app.defs.enums import MovingState, ObjectType


@register_command()
class UndockingCommand(BaseCommand):
    name = 'undocking'

    def __init__(self):
        super().__init__()
        self.progress: float = 0.0

    def update(self):
        if self.finished:
            return
        
        fleet = self.fleet
        moving_state = fleet.moving_state
        
        if moving_state != MovingState.Docked and moving_state != MovingState.Maneuvering:
            self.finished = True
            return
        
        
        fleet.moving_state = MovingState.Maneuvering
        self.progress += (dt / (Consts.DockingTime * 0.5))

        if self.progress >= 1.0:
            fleet.moving_state = MovingState.Idle
            if fleet.attached_to_type == ObjectType.Platform:
                platform = self.world.find_platform(fleet.attached_to_id)
                fleet.detach(platform)
            self.finished = True

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['progress'] = self.progress
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.progress = data.get('progress', 0.0)

    def cancel(self):
        if self.fleet.moving_state == MovingState.Maneuvering:
            self.fleet.moving_state = MovingState.Docked