from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from app.core.config import Consts
from app.core.types import ObjectType
from .base import BaseCommand
from .factory import register_command
from ..world import World
from app.utils import xy
from .move import MoveCommand

if TYPE_CHECKING:
    from ..ship import ShipEntity


@register_command()
class MoveToObjectCommand(BaseCommand):
    name = 'move_to_obj'

    def __init__(self, obj_id: Optional[int] = None, obj_type: Optional[ObjectType] = None):
        super().__init__()
        self.obj_id = obj_id
        self.obj_type = obj_type
        self.move_command = None

    def _prepare(self, ship: ShipEntity, world: World):
        match self.obj_type:
            case ObjectType.Platform:
                platform = world.find_platform(self.obj_id)
                if platform is None:
                    self.finished = True
                    return                
            
                x, y = xy.point_at_distance(
                    platform.x, 
                    platform.y, 
                    ship.pos.x, 
                    ship.pos.y, 
                    Consts.ObjectRadius * 0.9
                )
                self.move_command = MoveCommand(x, y)
            case ObjectType.Site:
                self.finished = True
                return

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.move_command is None:
            self._prepare(ship, world)
            if self.finished:
                return
        
        self.move_command.update(ship, dt, world)
        self.finished = self.move_command.finished

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['obj_id'] = self.obj_id
        data['obj_type'] = self.obj_type
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.obj_id = data.get('obj_id')
        self.obj_type = ObjectType(data.get('obj_type'))