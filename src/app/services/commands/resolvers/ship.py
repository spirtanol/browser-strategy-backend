from .base import ResolverContext, ResolveResult
from app.entities.user import UserEntity
from ..handlers.base import ShipTargeted


async def ship_command_resolver(context: ResolverContext, user: UserEntity, dto: ShipTargeted) -> ResolveResult:
    ship = await context.client_ship_service.find(dto.ship_id)
    if ship is None:
        return ResolveResult(
            success=False,
            message=f'Корабля {dto.ship_id} не существует'
        )

    if ship.owner_id != user.id:
        return ResolveResult(
            success=False,
            message=f'Пользователь {user.id} не владеет кораблем {ship.id}'
        )

    return ResolveResult(success=True)