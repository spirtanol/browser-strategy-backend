from .base import ResolverContext, CommandResolvingError
from app.entities.player import PlayerEntity
from ..handlers.fishing import FishingCommandParams
from .fleet_resolver import fleet_command_resolver 
from app.defs.enums import ObjectType


async def fishing_resolver(context: ResolverContext, player: PlayerEntity, dto: FishingCommandParams):
    await fleet_command_resolver(context, player, dto)
    
    fishing_site = await context.client_site_service.find(dto.site_id)

    if fishing_site is None:
        raise CommandResolvingError(dto, f'Объект {dto.site_id} не существует')

    if fishing_site.get_type() != ObjectType.Site:
        raise CommandResolvingError(dto, f'{dto.site_id} не рыбное место')