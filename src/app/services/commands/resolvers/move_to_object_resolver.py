from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.move_to_object import MoveToObjectCommandParams, ObjectType
from .ship import ship_command_resolver


async def move_to_object_resolver(context: ResolverContext, user: UserEntity, dto: MoveToObjectCommandParams):
    await ship_command_resolver(context, user, dto)
    
    match dto.obj_type:
        case ObjectType.Platform:
            if await context.client_platform_service.exists(dto.obj_id):
                return
        case ObjectType.Site:
            if await context.client_site_service.exists(dto.obj_id):
                return

    raise CommandResolvingError(dto, f'Объект {dto.obj_type}:{dto.obj_id} не существует')
    