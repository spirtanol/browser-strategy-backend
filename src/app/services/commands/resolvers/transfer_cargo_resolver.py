from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.transfer_cargo import TransferCargoCommandParams
from .fleet_resolver import fleet_command_resolver
from app.defs.items import MAP as ItemMap


async def transfer_cargo_resolver(
    context: ResolverContext,
    user: UserEntity,
    dto: TransferCargoCommandParams,
):
    await fleet_command_resolver(context, user, dto)

    fleet_a = await context.client_fleet_service.find(dto.fleet_id)
    if fleet_a is None:
        raise CommandResolvingError(dto, f'Флота {dto.fleet_id} не существует')

    ships_a = {ship.id for ship in fleet_a.ships}
    errors = []

    if dto.target_fleet_id is None:
        ship_ids = ships_a
    else:
        if dto.target_fleet_id == dto.fleet_id:
            raise CommandResolvingError(dto, f'Флот {dto.fleet_id} не может быть целью сам для себя')

        fleet_b = await context.client_fleet_service.find(dto.target_fleet_id)
        if fleet_b is None:
            raise CommandResolvingError(dto, f'Флота {dto.target_fleet_id} не существует')

        if fleet_b.owner_id != user.id:
            raise CommandResolvingError(
                dto,
                f'Пользователь {user.id} не владеет флотом {fleet_b.id}',
            )

        ship_ids = ships_a | {ship.id for ship in fleet_b.ships}

    for op in dto.operations:
        if op['item_name'] not in ItemMap:
            errors.append(f'Предмета {op["item_name"]} не существует')

        if op['from_ship_id'] == op['to_ship_id']:
            errors.append(f'Нельзя передать груз с корабля {op["from_ship_id"]} на него же')

        if op['from_ship_id'] not in ship_ids:
            errors.append(f'Корабль {op["from_ship_id"]} не входит в доступные флоты')

        if op['to_ship_id'] not in ship_ids:
            errors.append(f'Корабль {op["to_ship_id"]} не входит в доступные флоты')

    if errors:
        raise CommandResolvingError(dto, '\n'.join(errors))
