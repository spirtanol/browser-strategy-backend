from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypedDict, Any

from .base import BaseCommand
from ..world import World
from app.defs.enums import SiteContent, ObjectType, MovingState
from app.utils import xy
from app.defs import consts as Consts
from .move_to_object import MoveToObjectCommand
from app.defs import items as ItemDefs
from .factory import register_command

if TYPE_CHECKING:
    from ..site import SiteEntity


class FillLimit(TypedDict):
    ship_id: int
    limit: int

@register_command()
class FishingCommand(BaseCommand):
    name = 'fishing'

    def __init__(self, site_id: int = 0, fill_limits: Optional[list[FillLimit]] = None):
        super().__init__()
        self.site_id: int = site_id
        self.fill_limits = fill_limits if fill_limits else []
        self.site: Optional[SiteEntity] = None
        self._progress: float = 0.0
        self._finished_targets = set()

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['site_id'] = self.site_id
        data['fill_limits'] = self.fill_limits
        data['progress'] = self._progress
        data['finished_targets'] = list(self._finished_targets)
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.site_id = data.get('site_id', 0)
        self.fill_limits = data.get('fill_limits', [])
        self._progress = data.get('progress', 0.0)
        self._finished_targets = set(data.get('finished_targets', []))

    def update(self, dt: float):
        if self.finished:
            return

        if self.site is None:
            self.site = self.world.find_site(self.site_id)
            if self.site is None or self.site.site_content != SiteContent.Fish:
                self.finished = True
                return

        fleet = self.fleet
        
        if fleet.attached_to_type != ObjectType.Site or fleet.attached_to_id != self.site_id:
            distance = xy.distance(fleet.pos.x, fleet.pos.y, self.site.x, self.site.y)

            if distance < Consts.ObjectRadius:
                fleet.attach_to(self.site)
                fleet.moving_state = MovingState.Fishing
            else:
                move_command = MoveToObjectCommand(self.site_id, ObjectType.Site)
                move_command.is_dependent = True
                fleet.command_queue.add(move_command, True)
        else:
            self._progress += (dt / Consts.HarvestingCycle)

            if self._progress >= 1.0:
                self._progress -= 1.0
                extraction_quantity = int(fleet.get_net_value(ItemDefs.NetworkResource.HarvestingFish) * self.site.efficiency / ItemDefs.Fish.weight)
                items_left = extraction_quantity

                for fill_limit in self.fill_limits:
                    if items_left <= 0:
                        break
                    
                    ship_id, limit = fill_limit['ship_id'], fill_limit['limit']

                    if ship_id in self._finished_targets:
                        continue

                    ship = self.fleet.ships.get(ship_id, None)
                    if ship is None:
                        self._finished_targets.add(ship_id)
                        continue
                    
                    no_space = False
                    items_fit = items_left

                    if limit > 0:
                        limit_left = limit - ship.storage.get_amount(ItemDefs.Fish)
                        
                        if limit_left <= 0:
                            self._finished_targets.add(ship_id)        
                            continue

                        if limit_left <= items_fit:
                            items_fit = limit_left
                            no_space = True

                    fitted = ship.fit_quantity(ItemDefs.Fish, items_fit)
                    if fitted < items_fit:
                        no_space = True
                    items_fit = fitted

                    if items_fit > 0:
                        ship.storage.push(ItemDefs.Fish, items_fit)
                        self.site.reserve -= items_fit * ItemDefs.Fish.weight
                        items_left -= items_fit

                    if no_space:
                        self._finished_targets.add(ship_id)

            for fill_limit in self.fill_limits:
                if fill_limit['ship_id'] not in self._finished_targets:
                    return

            self.finished = True
            fleet.moving_state = MovingState.Idle
            fleet.detach(self.site)
            return

    def cancel(self):
        if self.fleet.moving_state == MovingState.Fishing:
            self.fleet.moving_state = MovingState.Idle