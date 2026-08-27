from __future__ import annotations
from typing import Optional, TYPE_CHECKING, override

from app.defs.enums import SiteType, SiteContent
from app.defs.deposites import Restriction
from .anchor_point import AnchorPointEntity
from app.defs.consts import SiteRecoveryCycle
from app.defs.enums import ObjectType

if TYPE_CHECKING:
    from .area import AreaEntity
    from .world import World

class SiteEntity(AnchorPointEntity):
    def __init__(self, restriction: Optional[Restriction] = None):
        super().__init__()
        self.x: float = 0.0
        self.y: float = 0.0
        self.site_type = SiteType.STABLE
        self.site_content = SiteContent.Fish
        self.restriction = restriction
        self.reserve = restriction.max_reserve if restriction else 0.0
        self.area: Optional[AreaEntity] = None

    @property
    def efficiency(self) -> float:
        if self.restriction.max_reserve <= 0:
            return self.restriction.min_efficiency

        fill_ratio = self.reserve / (self.restriction.max_reserve * self.restriction.max_efficiency_threshold)
        fill_ratio = max(0.0, min(1.0, fill_ratio))

        efficiency_range = self.restriction.max_efficiency - self.restriction.min_efficiency
        return self.restriction.min_efficiency + efficiency_range * fill_ratio

    def update(self, dt: float):
        recovery = self.restriction.recovery_rate * (dt / SiteRecoveryCycle)
        self.reserve = min(self.restriction.max_reserve, self.reserve + recovery)

    def get_type(self) -> ObjectType:
        return ObjectType.Site

    @override
    def bind_to_world(self, world: World):
        super().bind_to_world(world)
        area = world.get_area_at(self.x, self.y)
        if area is not None:
            area.bind_site(self)