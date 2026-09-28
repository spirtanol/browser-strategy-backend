from __future__ import annotations
from typing import override, TYPE_CHECKING

from .base import MapEntity
from app.defs.enums import ObjectType
from app.defs.consts import DirectDetectionRadius
from app.utils import xy

if TYPE_CHECKING:
    from .fleet import FleetEntity
    from .platform import PlatformEntity
    from .site import SiteEntity
    from .player import PlayerEntity

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

    def player_sees_fleet(self, player_id: int, target: FleetEntity) -> bool:
        for sensor in self.fleets.values():
            if sensor.owner_id != player_id or sensor.id == target.id:
                continue
            if xy.distance(sensor.pos.x, sensor.pos.y, target.pos.x, target.pos.y) <= DirectDetectionRadius:
                return True
        for platform in self.platforms.values():
            if platform.owner_id != player_id:
                continue
            if xy.distance(platform.x, platform.y, target.pos.x, target.pos.y) <= DirectDetectionRadius:
                return True
        return False

    def _detecting_sensor(self, player_id: int, target: FleetEntity) -> FleetEntity | PlatformEntity | None:
        for sensor in self.fleets.values():
            if sensor.owner_id != player_id or sensor.id == target.id:
                continue
            if xy.distance(sensor.pos.x, sensor.pos.y, target.pos.x, target.pos.y) <= DirectDetectionRadius:
                return sensor
        for platform in self.platforms.values():
            if platform.owner_id != player_id:
                continue
            if xy.distance(platform.x, platform.y, target.pos.x, target.pos.y) <= DirectDetectionRadius:
                return platform
        return None

    def _set_contact(self, player: PlayerEntity, fleet: FleetEntity, visible: bool) -> None:
        if player.map is None:
            return

        if visible:
            sensor = self._detecting_sensor(player.id, fleet)
            if sensor is None:
                return
            player.map.discover_fleet(fleet, sensor)
        else:
            player.map.lose_fleet(fleet)

    def _refresh_fleet_contacts(self) -> None:
        owner_ids: set[int] = set()
        for fleet in self.fleets.values():
            owner_ids.add(fleet.owner_id)
        for platform in self.platforms.values():
            owner_ids.add(platform.owner_id)

        for owner_id in owner_ids:
            owner = self.world.find_player(owner_id)
            if owner is None or owner.map is None or owner.is_npc:
                continue

            for fleet in self.fleets.values():
                if fleet.owner_id == owner_id:
                    continue
                self._set_contact(owner, fleet, self.player_sees_fleet(owner_id, fleet))

    def _scan_fleet(self, fleet: FleetEntity) -> None:
        player = self.world.find_player(fleet.owner_id)
        if player is None or player.is_npc or player.map is None:
            return

        for site in self.sites.values():
            if xy.distance(fleet.pos.x, fleet.pos.y, site.x, site.y) <= DirectDetectionRadius:
                player.map.discover_site(site, fleet)

        for platform in self.platforms.values():
            if platform.owner_id == fleet.owner_id:
                continue

            if xy.distance(fleet.pos.x, fleet.pos.y, platform.x, platform.y) <= DirectDetectionRadius:
                player.map.discover_platform(platform, fleet)

    def update(self, dt: float):
        self._refresh_fleet_contacts()
        for fleet in self.fleets.values():
            if not fleet.pos_cached:
                self._scan_fleet(fleet)

    def bind_fleet(self, fleet: FleetEntity):
        self.fleets[fleet.id] = fleet
        fleet.area = self
        fleet.pos_cached = False
        self._scan_fleet(fleet)
        player = self.world.find_player(fleet.owner_id)
        if player is not None and not player.is_npc and player.map is not None:
            player.map.discover_area(self, fleet)

    def unbind_fleet(self, fleet: FleetEntity):
        del self.fleets[fleet.id]
        self.world.on_fleet_left_area(fleet)
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
