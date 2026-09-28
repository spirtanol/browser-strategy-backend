from __future__ import annotations
from typing import TYPE_CHECKING

from app.defs.journal import (
    site_discovered,
    platform_discovered,
    area_discovered,
    fleet_discovered,
    fleet_lost,
)

if TYPE_CHECKING:
    from .fleet import FleetEntity
    from .site import SiteEntity
    from .platform import PlatformEntity
    from .area import AreaEntity


class PlayerMapEntity:
    def __init__(self):
        self.player_id: int = 0
        self.areas: set[int] = set()
        self.sites: set[int] = set()
        self.platforms: set[int] = set()
        self.fleets: set[int] = set()
        self.map_cached: bool = False

    def add_fleet(self, fleet_id: int) -> None:
        if fleet_id in self.fleets:
            return
        self.fleets.add(fleet_id)
        self.map_cached = False

    def remove_fleet(self, fleet_id: int) -> None:
        if fleet_id not in self.fleets:
            return
        self.fleets.remove(fleet_id)
        self.map_cached = False

    def discover_fleet(self, fleet: FleetEntity, sensor: FleetEntity | PlatformEntity) -> None:
        if fleet.id in self.fleets:
            return
        self.fleets.add(fleet.id)
        self.map_cached = False
        fleet.world.emit_journal_event(fleet_discovered(self.player_id, fleet, sensor))

    def lose_fleet(self, fleet: FleetEntity) -> None:
        if fleet.id not in self.fleets:
            return
        self.fleets.remove(fleet.id)
        self.map_cached = False
        fleet.world.emit_journal_event(fleet_lost(self.player_id, fleet))

    def discover_site(self, site: SiteEntity, fleet: FleetEntity) -> None:
        if site.id in self.sites:
            return
        self.sites.add(site.id)
        self.map_cached = False
        fleet.world.emit_journal_event(site_discovered(fleet, site))

    def discover_platform(self, platform: PlatformEntity, fleet: FleetEntity) -> None:
        if platform.id in self.platforms:
            return
        self.platforms.add(platform.id)
        self.map_cached = False
        fleet.world.emit_journal_event(platform_discovered(fleet, platform))

    def discover_area(self, area: AreaEntity, fleet: FleetEntity) -> None:
        if area.id in self.areas:
            return
        self.areas.add(area.id)
        self.map_cached = False
        fleet.world.emit_journal_event(area_discovered(fleet, area))
