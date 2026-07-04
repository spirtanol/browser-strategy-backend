from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.dock_to_platform import DockToPlatformCommandParams
from .ship import ship_command_resolver


async def dock_to_platform_resolver(context: ResolverContext, user: UserEntity, dto: DockToPlatformCommandParams):
    await ship_command_resolver(context, user, dto)
    
    platform = await context.client_platform_service.exists(dto.platform_id)
    if platform is None:
        raise CommandResolvingError(dto, f'Платформа {dto.platform_id} не существует')