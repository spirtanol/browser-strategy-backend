from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

import app.defs.consts as Consts
from app.defs.enums import ObjectType
from .base import BaseCommand
from .factory import register_command
from ..world import World
from app.utils import xy
from .move import MoveCommand


@register_command()
class MoveToObjectCommand(BaseCommand):
    name = 'move_to_obj'

    def __init__(self, obj_id: Optional[int] = None, obj_type: Optional[ObjectType] = None):
        super().__init__()
        self.obj_id = obj_id
        self.obj_type = obj_type

    def update(self):
        if self.finished:
            return

        fleet = self.fleet

        match self.obj_type:
            case ObjectType.Platform:
                platform = self.world.find_platform(self.obj_id)
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

                destX = site.x
                destY = site.y
            case _:
                self.finished = True
                return

        distance = xy.distance(fleet.pos.x, fleet.pos.y, destX, destY)

        if distance < Consts.ObjectRadius:
            self.finished = True
            return

        x, y = xy.point_at_distance(
            destX, 
            destY, 
            fleet.pos.x, 
            fleet.pos.y, 
            Consts.ObjectRadius * 0.9
        )
        move_command = MoveCommand(x, y)
        move_command.is_dependent = True
        self.queue.add(move_command, True)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['obj_id'] = self.obj_id
        data['obj_type'] = self.obj_type
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.obj_id = data.get('obj_id')
        self.obj_type = ObjectType(data.get('obj_type'))
