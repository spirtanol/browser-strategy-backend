from .base import ResolverContext, CommandResolvingError
from app.entities.player import PlayerEntity
from ..handlers.dock_to_platform import DockToPlatformCommandParams
from .fleet_resolver import fleet_command_resolver


async def dock_to_platform_resolver(context: ResolverContext, player: PlayerEntity, dto: DockToPlatformCommandParams):
    await fleet_command_resolver(context, player, dto)
    
    platform = await context.client_platform_service.exists(dto.platform_id)
    if platform is None:
        raise CommandResolvingError(dto, f'Платформа {dto.platform_id} не существует')