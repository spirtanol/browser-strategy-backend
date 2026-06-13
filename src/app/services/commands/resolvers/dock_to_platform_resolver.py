from .base import ResolverContext, ResolveResult
from app.entities.user import UserEntity
from ..handlers.dock_to_platform import DockToPlatformCommandParams
from .ship import ship_command_resolver


async def dock_to_platform_resolver(context: ResolverContext, user: UserEntity, dto: DockToPlatformCommandParams) -> ResolveResult:
    res = await ship_command_resolver(context, user, dto)
    
    if not res.success:
        return res

    if await context.client_platform_service.exists(dto.platform_id):
        return ResolveResult(success=True)

    return ResolveResult(
        success=False,
        message=f'Платформа {dto.platform_id} не существует'
    )