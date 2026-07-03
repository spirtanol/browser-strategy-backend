from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .base import BaseCommand
from ..world import World
from app.defs.enums import SiteContent, ObjectType, MovingState
from app.utils import xy
from app.defs import consts as Consts
from .move_to_object import MoveToObjectCommand
from app.defs import items as ItemDefs
from .factory import register_command

if TYPE_CHECKING:
    from ..ship import ShipEntity
    from ..site import SiteEntity


@register_command()
class FishingCommand(BaseCommand):
    name = 'fishing'

    def __init__(self, site_id: int = 0, target_quantity: int = 0):
        super().__init__()
        self.site_id: int = site_id
        self.target_quantity = target_quantity
        self.site: Optional[SiteEntity] = None
        self._progress: float = 0.0

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['site_id'] = self.site_id
        data['target_quantity'] = self.target_quantity
        data['progress'] = self._progress
        return data

    def from_dict(self, data: dict[str, any]):
        super().from_dict(data)
        self.site_id = data.get('site_id', 0)
        self.target_quantity = data.get('target_quantity', 0)
        self._progress = data.get('progress', 0.0)

    def update(self, ship: ShipEntity, dt: float, world: World):
        if self.finished:
            return

        if self.site is None:
            self.site = world.find_site(self.site_id)
            if self.site is None or self.site.site_content != SiteContent.Fish:
                self.finished = True
                return
        
        if ship.attached_to_type != ObjectType.Site or ship.attached_to_id != self.site_id:
            distance = xy.distance(ship.pos.x, ship.pos.y, self.site.x, self.site.y)

            if distance < Consts.ObjectRadius:
                ship.attach_to(self.site)
                ship.moving_state = MovingState.Fishing
            else:
                move_command = MoveToObjectCommand(self.site_id, ObjectType.Site)
                move_command.is_dependend = True
                ship.command_queue.add(move_command, True)
        else:
            self._progress += dt
            if self._progress >= Consts.HarvestingCycle:
                self._progress -= Consts.HarvestingCycle
                extraction_quantity = ship.get_net(ItemDefs.NetworkResource.HarvestingFish).value * self.site.efficiency
                self.site.reserve -= extraction_quantity
                fish_quantity = int(extraction_quantity * 1000 / ItemDefs.Fish.weight)
                ship.storage.push(ItemDefs.Fish, fish_quantity)

            if (ship.storage.get_amount(ItemDefs.Fish) >= self.target_quantity):
                self.finished = True
                ship.moving_state = MovingState.Idle
                ship.detach(self.site)
                return
            