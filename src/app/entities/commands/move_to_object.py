from __future__ import annotations
from typing import Optional, Any

import app.defs.consts as Consts
from app.defs.enums import ObjectType, SiteContent
from .base import BaseCommand
from .factory import register_command
from app.utils import xy
from .move import MoveCommand
from app.defs.journal import move_to_obj_arrived, move_to_obj_started


@register_command()
class MoveToObjectCommand(BaseCommand):
    name = 'move_to_obj'

    def __init__(self, obj_id: Optional[int] = None, obj_type: Optional[ObjectType] = None):
        super().__init__()
        self.obj_id = obj_id
        self.obj_type = obj_type
        self._logged_start = False

    def update(self, dt: float):
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
                obj_name = platform.name or None
                site_content = None
            case ObjectType.Site:
                site = self.world.find_site(self.obj_id)
                if site is None:
                    self.finished = True
                    return

                destX = site.x
                destY = site.y
                obj_name = None
                site_content = site.site_content
            case ObjectType.Fleet:
                target = self.world.find_fleet(self.obj_id)
                if target is None or target.id == fleet.id:
                    self.finished = True
                    return

                distance = xy.distance(fleet.pos.x, fleet.pos.y, target.pos.x, target.pos.y)
                if distance <= Consts.ObjectRadius:
                    self._emit_arrived(target.name or None)
                    self.finished = True
                    return

                step = min(Consts.ObjectRadius * 0.95, distance)
                x, y = xy.point_at_distance(
                    fleet.pos.x,
                    fleet.pos.y,
                    target.pos.x,
                    target.pos.y,
                    step,
                )
                self._emit_started(target.name or None)
                move_command = MoveCommand(x, y)
                move_command.is_dependent = True
                self.queue.add(move_command, True)
                return
            case _:
                self.finished = True
                return

        distance = xy.distance(fleet.pos.x, fleet.pos.y, destX, destY)

        if distance < Consts.ObjectRadius:
            self._emit_arrived(obj_name, site_content)
            self.finished = True
            return

        x, y = xy.point_at_distance(
            destX,
            destY,
            fleet.pos.x,
            fleet.pos.y,
            Consts.ObjectRadius * 0.9,
        )
        self._emit_started(obj_name, site_content)
        move_command = MoveCommand(x, y)
        move_command.is_dependent = True
        self.queue.add(move_command, True)

    def _emit_started(self, obj_name: Optional[str], site_content: Optional[SiteContent] = None):
        if self._logged_start:
            return
        self._logged_start = True
        self.world.emit_journal_event(
            move_to_obj_started(self.fleet, self.obj_id, self.obj_type, obj_name, site_content)
        )

    def _emit_arrived(self, obj_name: Optional[str], site_content: Optional[SiteContent] = None):
        self.world.emit_journal_event(
            move_to_obj_arrived(self.fleet, self.obj_id, self.obj_type, obj_name, site_content)
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['obj_id'] = self.obj_id
        data['obj_type'] = self.obj_type
        data['logged_start'] = self._logged_start
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.obj_id = data.get('obj_id')
        self.obj_type = ObjectType(data.get('obj_type'))
        self._logged_start = data.get('logged_start', False)
