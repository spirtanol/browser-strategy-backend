from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .event import JournalEvent
from ..enums import JournalEmitterType, JournalSeverity, ObjectType, SiteContent

if TYPE_CHECKING:
    from app.entities.area import AreaEntity
    from app.entities.fleet import FleetEntity
    from app.entities.platform import PlatformEntity
    from app.entities.site import SiteEntity


def starvation_begins(fleet: FleetEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='starvation_begins',
        severity=JournalSeverity.Dangerous,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name
        }
    )

def commands_complete(fleet: FleetEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='commands_complete',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name
        }
    )


def move_started(fleet: FleetEntity, x: float, y: float) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='move_started',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name,
            'x': x,
            'y': y,
        }
    )


def move_arrived(fleet: FleetEntity, x: float, y: float) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='move_arrived',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name,
            'x': x,
            'y': y,
        }
    )


def _move_to_obj_params(
    fleet: FleetEntity,
    obj_id: Optional[int],
    obj_type: Optional[ObjectType],
    obj_name: Optional[str],
    site_content: Optional[SiteContent],
) -> dict:
    return {
        'fleet_id': fleet.id,
        'fleet_name': fleet.name,
        'obj_id': obj_id,
        'obj_type': int(obj_type) if obj_type is not None else None,
        'obj_name': obj_name,
        'site_content': int(site_content) if site_content is not None else None,
    }


def move_to_obj_started(
    fleet: FleetEntity,
    obj_id: Optional[int],
    obj_type: Optional[ObjectType],
    obj_name: Optional[str] = None,
    site_content: Optional[SiteContent] = None,
) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='move_to_obj_started',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params=_move_to_obj_params(fleet, obj_id, obj_type, obj_name, site_content),
    )


def move_to_obj_arrived(
    fleet: FleetEntity,
    obj_id: Optional[int],
    obj_type: Optional[ObjectType],
    obj_name: Optional[str] = None,
    site_content: Optional[SiteContent] = None,
) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='move_to_obj_arrived',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params=_move_to_obj_params(fleet, obj_id, obj_type, obj_name, site_content),
    )


def _dock_params(fleet: FleetEntity, platform: PlatformEntity) -> dict:
    return {
        'fleet_id': fleet.id,
        'fleet_name': fleet.name,
        'platform_id': platform.id,
        'platform_name': platform.name,
    }


def dock_started(fleet: FleetEntity, platform: PlatformEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='dock_started',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params=_dock_params(fleet, platform),
    )


def docked(fleet: FleetEntity, platform: PlatformEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='docked',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params=_dock_params(fleet, platform),
    )


def _trade_operations(operations: list) -> list[dict]:
    return [
        {
            'item_name': op['item_name'],
            'quantity': op['quantity'],
            'price': op['price'],
            'op_type': int(op['op_type']),
        }
        for op in operations
    ]


def trade_started(fleet: FleetEntity, platform: PlatformEntity, operations: list) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='trade_started',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            **_dock_params(fleet, platform),
            'operations': _trade_operations(operations),
        },
    )


def trade_completed(
    fleet: FleetEntity,
    platform: PlatformEntity,
    operations: list,
    fills: list[dict],
) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='trade_completed',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            **_dock_params(fleet, platform),
            'operations': _trade_operations(operations),
            'fills': fills,
        },
    )


def site_discovered(fleet: FleetEntity, site: SiteEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='site_discovered',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name,
            'site_id': site.id,
            'x': site.x,
            'y': site.y,
            'site_content': int(site.site_content),
        },
    )


def platform_discovered(fleet: FleetEntity, platform: PlatformEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='platform_discovered',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name,
            'platform_id': platform.id,
            'platform_name': platform.name,
            'x': platform.x,
            'y': platform.y,
        },
    )


def fleet_discovered(
    player_id: int,
    fleet: FleetEntity,
    sensor: FleetEntity | PlatformEntity,
) -> JournalEvent:
    owner = fleet.world.find_player(fleet.owner_id)
    if sensor.get_type() == ObjectType.Platform:
        emitter_type = JournalEmitterType.Platform
    else:
        emitter_type = JournalEmitterType.Fleet
    return JournalEvent(
        user_id=player_id,
        event_type='fleet_discovered',
        severity=JournalSeverity.Info,
        emitter_id=sensor.id,
        emitter_type=emitter_type,
        params={
            'fleet_id': fleet.id,
            'x': fleet.pos.x,
            'y': fleet.pos.y,
            'owner_id': fleet.owner_id,
            'owner_name': owner.name if owner is not None else '',
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'sensor_kind': int(sensor.get_type()),
        },
    )


def fleet_lost(player_id: int, fleet: FleetEntity) -> JournalEvent:
    return JournalEvent(
        user_id=player_id,
        event_type='fleet_lost',
        severity=JournalSeverity.Info,
        params={
            'fleet_id': fleet.id,
            'x': fleet.pos.x,
            'y': fleet.pos.y,
        },
    )


def area_discovered(fleet: FleetEntity, area: AreaEntity) -> JournalEvent:
    return JournalEvent(
        user_id=fleet.owner_id,
        event_type='area_discovered',
        severity=JournalSeverity.Info,
        emitter_id=fleet.id,
        emitter_type=JournalEmitterType.Fleet,
        params={
            'fleet_id': fleet.id,
            'fleet_name': fleet.name,
            'area_id': area.id,
            'area_name': area.name,
            'x': area.x,
            'y': area.y,
        },
    )