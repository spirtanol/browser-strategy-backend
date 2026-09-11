from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .event import JournalEvent
from ..enums import JournalEmitterType, JournalSeverity, ObjectType, SiteContent

if TYPE_CHECKING:
    from app.entities.fleet import FleetEntity
    from app.entities.platform import PlatformEntity


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