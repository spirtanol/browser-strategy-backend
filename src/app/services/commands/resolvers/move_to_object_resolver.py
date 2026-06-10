from .base import ResolverContext, ResolveResult
from app.entities.user import UserEntity
from ..handlers.move_to_object import MoveToObjectCommandParams, ObjectType
from .ship import ship_command_resolver


async def move_to_object_resolver(context: ResolverContext, user: UserEntity, dto: MoveToObjectCommandParams) -> ResolveResult:
    res = await ship_command_resolver(context, user, dto)
    
    if not res.success:
        return res

    match dto.obj_type:
        case ObjectType.Platform:
            if await context.client_platform_service.exists(dto.obj_id):
                return ResolveResult(success=True)

    return ResolveResult(
        success=False,
        message=f'Объект {dto.obj_type}:{dto.obj_id} не существует'
    )