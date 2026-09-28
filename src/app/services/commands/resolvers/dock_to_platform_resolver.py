from .base import ResolverContext
from app.entities.player import PlayerEntity
from app.defs.enums import ObjectType
from ..handlers.dock_to_platform import DockToPlatformCommandParams
from ..handlers.move_to_object import MoveToObjectCommandParams
from .move_to_object_resolver import move_to_object_resolver


async def dock_to_platform_resolver(context: ResolverContext, player: PlayerEntity, dto: DockToPlatformCommandParams):
    await move_to_object_resolver(context, player, MoveToObjectCommandParams(
        id=dto.id,
        fleet_id=dto.fleet_id,
        obj_id=dto.platform_id,
        obj_type=ObjectType.Platform,
        clear_queue=dto.clear_queue,
        on_top=dto.on_top,
    ))
