from typing import Optional

from app.defs.enums import SiteType, SiteContent
from .world import World
from app.defs.deposites import Restriction
from .anchor_point import AnchorPoint, ObjectType


_RECOVERY_CYCLE = 24 * 60 * 60

class SiteEntity(AnchorPoint):
    def __init__(self, id: int = 0, restriction: Optional[Restriction] = None):
        self.id = id
        self.x: float = 0.0
        self.y: float = 0.0
        self.site_type = SiteType.STABLE
        self.site_content = SiteContent.Fish
        self.restriction = restriction
        self.reserve = restriction.max_reserve if restriction else 0.0
        self.attached_ships: set[int] = set()

    @property
    def efficiency(self) -> float:
        if self.restriction.max_reserve <= 0:
            return self.restriction.min_efficiency

        fill_ratio = self.reserve / self.restriction.max_reserve
        fill_ratio = max(0.0, min(1.0, fill_ratio))

        efficiency_range = self.restriction.max_efficiency - self.restriction.min_efficiency
        return self.restriction.min_efficiency + efficiency_range * fill_ratio

    def update(self, dt: float, world: World):
        recovery = self.restriction.recovery_rate * dt / _RECOVERY_CYCLE
        self.reserve = min(self.restriction.max_reserve, self.reserve + recovery)

    def get_type(self) -> ObjectType:
        return ObjectType.Site

    def attach_ship(self, ship_id: int) -> None:
        self.attached_ships.add(ship_id)

    def detach_ship(self, ship_id: int) -> None:
        self.attached_ships.remove(ship_id)

    def get_id(self) -> int:
        return self.id