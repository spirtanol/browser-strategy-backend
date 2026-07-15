from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.base import FleetTargeted


async def fleet_command_resolver(context: ResolverContext, user: UserEntity, dto: FleetTargeted):
    fleet = await context.client_fleet_service.find(dto.fleet_id)
    if fleet is None:
        raise CommandResolvingError(dto, f'Флота {dto.fleet_id} не существует')

    if fleet.owner_id != user.id:
        raise CommandResolvingError(dto, f'Пользователь {user.id} не владеет флотом {fleet.id}')
