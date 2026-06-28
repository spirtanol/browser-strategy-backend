from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .base import BaseCommand
from ..world import World

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

        #if self.site is None:
        #    self.site = world.