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

    fleet = await context.client_fleet_service.find(dto.fleet_id)
    if fleet is None:
        raise CommandResolvingError(dto, f'Флота {dto.fleet_id} не существует')

    ship_ids = {ship.id for ship in fleet.ships}
    errors = []

    for op in dto.operations:
        if op['item_name'] not in ItemMap:
            errors.append(f'Предмета {op["item_name"]} не существует')

        if op['from_ship_id'] == op['to_ship_id']:
            errors.append(f'Нельзя передать груз с корабля {op["from_ship_id"]} на него же')

        if op['from_ship_id'] not in ship_ids:
            errors.append(f'Корабль {op["from_ship_id"]} не входит во флот {fleet.id}')

        if op['to_ship_id'] not in ship_ids:
            errors.append(f'Корабль {op["to_ship_id"]} не входит во флот {fleet.id}')

    if errors:
        raise CommandResolvingError(dto, '\n'.join(errors))
