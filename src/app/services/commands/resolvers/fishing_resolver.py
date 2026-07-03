from .base import ResolverContext, ResolveResult
from app.entities.user import UserEntity
from ..handlers.fishing import FishingCommandParams
from .ship import ship_command_resolver
from app.defs.enums import ObjectType


async def fishing_resolver(context: ResolverContext, user: UserEntity, dto: FishingCommandParams) -> ResolveResult:
    res = await ship_command_resolver(context, user, dto)
    
    if not res.success:
        return res

    fishing_site = await context.client_site_service.find(dto.site_id)

    if fishing_site is None:
        return ResolveResult(
            success=False,
            message=f'Объект {dto.site_id} не существует'
        )

    if fishing_site.get_type() != ObjectType.Site:
        return ResolveResult(
            success=False,
            message=f'{dto.site_id} не рыбное место'
        )

    return ResolveResult(success=True)