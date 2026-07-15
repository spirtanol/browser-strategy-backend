from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

from .base import BaseCommand
from .factory import register_command
from .move_to_object import MoveToObjectCommand, ObjectType
import app.defs.consts as Consts
from ..world import World
from app.utils import xy
from app.defs.enums import MovingState


@register_command()
class DockingCommand(BaseCommand):
    name = 'docking'

    def __init__(self, platform_id: Optional[int] = None):
        super().__init__()
        self.platform_id = platform_id
        self.platform: Optional[PlatformEntity] = None
        self.docking_progress: float = 0.0
        self.stage = 0

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['platform_id'] = self.platform_id
        data['progress'] = self.docking_progress
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.platform_id = data.get('platform_id', 0)
        self.docking_progress = data.get('progress', 0.0)

    def get_platform(self) -> Optional[PlatformEntity]:
        if self.platform is None:
            self.platform = self.world.find_platform(self.platform_id)
        return self.platform

    def update(self, dt: float):
        if self.finished:
            return

        fleet = self.fleet

        match self.stage:
            case 0:
                platform = self.get_platform()
                if platform is None:
                    self.finished = True
                    return
                
                distance = xy.distance(fleet.pos.x, fleet.pos.y, platform.x, platform.y)
                if distance > Consts.ObjectRadius:
                    move_command = MoveToObjectCommand(self.platform_id, ObjectType.Platform)
                    move_command.is_dependent = True
                    fleet.command_queue.add(move_command, True)
                else:
                    self.stage = 1
            case 1:
                if fleet.moving_state == MovingState.Docked:
                    self.finished = True
                    platform = self.get_platform()
                    fleet.attach_to(platform)
                    return

                fleet.moving_state = MovingState.Maneuvering
                self.docking_progress += (dt / Consts.DockingTime)
                if self.docking_progress >= 1.0:
                    fleet.moving_state = MovingState.Docked
                    platform = self.get_platform()
                    fleet.attach_to(platform)
                    self.finished = True

    def cancel(self):
        if self.fleet.moving_state == MovingState.Maneuvering:
            self.fleet.moving_state = MovingState.Idle