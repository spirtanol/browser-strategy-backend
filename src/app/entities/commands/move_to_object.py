from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import app.defs.consts as Consts
from app.defs.enums import ObjectType
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

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished:
            return

        match self.obj_type:
            case ObjectType.Platform:
                platform = world.find_platform(self.obj_id)
                if platform is None:
                    self.finished = True
                    return

                destX = platform.x
                destY = platform.y
            case ObjectType.Site:
                site = world.find_site(self.obj_id)
                if site is None:
                    self.finished
                    return

                destX = platform.x
                destY = platform.y
            case _:
                self.finished = True
                return

        distance = xy.distance(ship.pos.x, ship.pos.y, destX, destY)

        if distance < Consts.ObjectRadius:
            self.finished = True
            return

        x, y = xy.point_at_distance(
            destX, 
            destY, 
            ship.pos.x, 
            ship.pos.y, 
            Consts.ObjectRadius * 0.9
        )
        move_command = MoveCommand(x, y)
        move_command.is_dependend = True
        ship.command_queue.add(move_command, True)

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['obj_id'] = self.obj_id
        data['obj_type'] = self.obj_type
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.obj_id = data.get('obj_id')
        self.obj_type = ObjectType(data.get('obj_type'))