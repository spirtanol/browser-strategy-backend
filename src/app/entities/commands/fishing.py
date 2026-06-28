from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .base import BaseCommand
from ..world import World
from app.defs.enums import SiteContent, ObjectType, MovingState
from app.utils import xy
from app.defs import consts as Consts
from .move_to_object import MoveToObjectCommand
from app.defs import items as ItemDefs

if TYPE_CHECKING:
    from ..ship import ShipEntity
    from ..site import SiteEntity


class FishingCommand(BaseCommand):
    name = 'fishing'

    def __init__(self, site_id: int = 0, target_quantity: int = 0):
        super().__init__()
        self.site_id: int = site_id
        self.target_quantity = target_quantity
        self.site: Optional[SiteEntity] = None

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['site_id'] = self.site_id
        data['target_quantity'] = self.target_quantity
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.site_id = data.get('site_id', 0)
        self.target_quantity = data.get('target_quantity', 0)

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished:
            return

        if self.site is None:
            self.site = world.find_site(self.site_id)
            if self.site is None or self.site.site_content != SiteContent.Fish:
                self.finished = True
                return
        
        if ship.attach_to_type != ObjectType.Site or ship.attached_to_id != self.site_id:
            distance = xy.distance(ship.pos.x, ship.pos.y, self.site.x, self.site.y)

            if distance < Consts.ObjectRadius:
                ship.attach_to(self.site)
            else:
                move_command = MoveToObjectCommand(self.site_id, ObjectType.Site)
                move_command.is_dependend = True
                ship.command_queue.add(move_command, True)
                ship.moving_state = MovingState.Fishing
        else:
            if (ship.storage.get_amount(ItemDefs.Fish) >= self.target_quantity):
                self.finished = True
                ship.moving_state = MovingState.Idle
                return
            