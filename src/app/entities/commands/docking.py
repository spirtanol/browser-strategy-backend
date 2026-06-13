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
        self.stage: int = 0
        self.platform_id = platform_id
        self.move_command = None
        self.platform: Optional[PlatformEntity] = None
        self.docking_progress: float = 0.0

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['platform_id'] = self.platform_id
        data['stage'] = self.stage
        data['progress'] = self.docking_progress
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.platform_id = data.get('platform_id', 0)
        self.stage = data.get('stage', 0)
        self.docking_progress = data.get('progress', 0.0)

    def get_platform(self, world: World) -> Optional[PlatformEntity]:
        if self.platform is None:
            self.platform = world.find_platform(self.platform_id)
        return self.platform

    def update(self, ship: ShipEntity, dt: float, world: World):
        match self.stage:
            case 0:
                if self.move_command is None:
                    platform = self.get_platform(world)
                    if platform is None:
                        self.finished = True
                        return
                    
                    distance = xy.distance(ship.pos.x, ship.pos.y, platform.x, platform.y)
                    if distance > Consts.ObjectRadius:
                        self.move_command = MoveToObjectCommand(self.platform_id, ObjectType.Platform)
                    else:
                        self.stage = 1
                if self.move_command:
                    self.move_command.update(ship, dt, world)
                    if self.move_command.finished:
                        self.move_command = None
                        self.stage = 1
            case 1:
                ship.state = MovingState.Maneuvering
                self.docking_progress += dt
                if self.docking_progress >= Consts.DockingTime:
                    ship.state = MovingState.Docked
                    platform = self.get_platform(world)
                    ship.attach_to(platform)
                    self.finished = True