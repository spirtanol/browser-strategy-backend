from .base import ResolverContext, CommandResolvingError
from app.entities.player import PlayerEntity
from app.defs.enums import ObjectType
from ..handlers.fishing import FishingCommandParams
from ..handlers.move_to_object import MoveToObjectCommandParams
from .move_to_object_resolver import move_to_object_resolver


async def fishing_resolver(context: ResolverContext, player: PlayerEntity, dto: FishingCommandParams):
    await move_to_object_resolver(context, player, MoveToObjectCommandParams(
        id=dto.id,
        fleet_id=dto.fleet_id,
        obj_id=dto.site_id,
        obj_type=ObjectType.Site,
        clear_queue=dto.clear_queue,
        on_top=dto.on_top,
    ))

    fishing_site = await context.client_site_service.find(dto.site_id)

    if fishing_site is None:
        raise CommandResolvingError(dto, f'Объект {dto.site_id} не существует')

    if fishing_site.get_type() != ObjectType.Site:
        raise CommandResolvingError(dto, f'{dto.site_id} не рыбное место')
