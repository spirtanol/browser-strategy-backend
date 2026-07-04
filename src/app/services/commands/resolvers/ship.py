from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.base import ShipTargeted


async def ship_command_resolver(context: ResolverContext, user: UserEntity, dto: ShipTargeted):
    ship = await context.client_ship_service.find(dto.ship_id)
    if ship is None:
        raise CommandResolvingError(dto, f'Крабля {dto.ship_id} не существует')

    if ship.owner_id != user.id:
        raise CommandResolvingError(dto, f'Пользователь {user.id} не владеет кораблем {ship.id}')
