from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .base import BaseCommand
from .factory import register_command
from .move_to_object import MoveToObjectCommand, ObjectType
from app.core.config import Consts
from ..world import World
from app.utils import xy
from app.core.types import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity
    from ..platform import PlatformEntity


@register_command()
class DockingCommand(BaseCommand):
    name = 'docking'

    def __init__(self, platform_id: Optional[int] = None):
        super().__init__()
        self.platform_id = platform_id
        self.platform: Optional[PlatformEntity] = None
        self.docking_progress: float = 0.0
        self.stage = 0

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['platform_id'] = self.platform_id
        data['progress'] = self.docking_progress
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.platform_id = data.get('platform_id', 0)
        self.docking_progress = data.get('progress', 0.0)

    def get_platform(self, world: World) -> Optional[PlatformEntity]:
        if self.platform is None:
            self.platform = world.find_platform(self.platform_id)
        return self.platform

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished:
            return

        match self.stage:
            case 0:
                platform = self.get_platform(world)
                if platform is None:
                    self.finished = True
                    return
                
                distance = xy.distance(ship.pos.x, ship.pos.y, platform.x, platform.y)
                if distance > Consts.ObjectRadius:
                    move_command = MoveToObjectCommand(self.platform_id, ObjectType.Platform)
                    move_command.is_dependend = True
                    ship.command_queue.add(move_command, True)
                else:
                    self.stage = 1
            case 1:
                if ship.state == MovingState.Docked:
                    self.finished = True
                    platform = self.get_platform(world)
                    ship.attach_to(platform)
                    return

                ship.state = MovingState.Maneuvering
                self.docking_progress += (dt / Consts.DockingTime)
                if self.docking_progress >= 1.0:
                    ship.state = MovingState.Docked
                    platform = self.get_platform(world)
                    ship.attach_to(platform)
                    self.finished = True