from .base import ResolverContext, CommandResolvingError
from app.entities.player import PlayerEntity
from ..handlers.base import FleetTargeted


async def fleet_command_resolver(context: ResolverContext, player: PlayerEntity, dto: FleetTargeted):
    fleet = await context.client_fleet_service.find(dto.fleet_id)
    if fleet is None:
        raise CommandResolvingError(dto, f'Флота {dto.fleet_id} не существует')

    if fleet.owner_id != player.id:
        raise CommandResolvingError(dto, f'Пользователь {player.id} не владеет флотом {fleet.id}')
