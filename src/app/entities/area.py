from __future__ import annotations
from typing import override, TYPE_CHECKING

from .base import MapEntity
from app.defs.enums import ObjectType

if TYPE_CHECKING:
    from .fleet import FleetEntity
    from .platform import PlatformEntity
    from .site import SiteEntity

class AreaEntity(MapEntity):
    def __init__(self):
        super().__init__()
        self.x = 0.0
        self.y = 0.0
        self.name = 'no name'
        self.empty_duration = 0
        self.fleets: dict[int, FleetEntity] = {}
        self.platforms: dict[int, PlatformEntity] = {}
        self.sites: dict[int, SiteEntity] = {}

    @override
    def get_type(self) -> ObjectType:
        return ObjectType.Area

    def bind_fleet(self, fleet: FleetEntity):
        self.fleets[fleet.id] = fleet
        fleet.area = self

    def unbind_fleet(self, fleet: FleetEntity):
        del self.fleets[fleet.id]
        fleet.area = None

    def bind_platform(self, platform: PlatformEntity):
        self.platforms[platform.id] = platform
        platform.area = self

    def unbind_platform(self, platform: PlatformEntity):
        del self.platforms[platform.id]
        platform.area = None

    def bind_site(self, site: SiteEntity):
        self.sites[site.id] = site
        site.area = self

    def unbind_site(self, site: SiteEntity):
        del self.sites[site.id]
        site.area = None