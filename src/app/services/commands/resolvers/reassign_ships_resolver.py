from .base import ResolverContext, CommandResolvingError
from app.entities.user import UserEntity
from ..handlers.reassign_ships import ReassignShipsCommandParams
from .fleet_resolver import fleet_command_resolver
from app.defs.enums import ShipReassignOpType


async def reassign_ships_resolver(
    context: ResolverContext,
    user: UserEntity,
    dto: ReassignShipsCommandParams,
):
    await fleet_command_resolver(context, user, dto)

    fleet_a = await context.client_fleet_service.find(dto.fleet_id)
    if fleet_a is None:
        raise CommandResolvingError(dto, f'Флота {dto.fleet_id} не существует')

    ships_a = {ship.id for ship in fleet_a.ships}
    errors = []

    if dto.target_fleet_id is None:
        for op in dto.operations:
            if op['op'] != ShipReassignOpType.Detach:
                errors.append(
                    f'При выделении флота операция для корабля {op["ship_id"]} должна быть Detach'
                )
                continue
            if op['ship_id'] not in ships_a:
                errors.append(f'Корабль {op["ship_id"]} не входит во флот {fleet_a.id}')
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

        ships_b = {ship.id for ship in fleet_b.ships}

        for op in dto.operations:
            try:
                op_type = ShipReassignOpType(op['op'])
            except ValueError:
                errors.append(f'Неизвестная операция {op["op"]} для корабля {op["ship_id"]}')
                continue

            if op_type == ShipReassignOpType.Detach:
                if op['ship_id'] not in ships_a:
                    errors.append(f'Корабль {op["ship_id"]} не входит во флот {fleet_a.id}')
            elif op_type == ShipReassignOpType.Attach:
                if op['ship_id'] not in ships_b:
                    errors.append(f'Корабль {op["ship_id"]} не входит во флот {fleet_b.id}')

    if errors:
        raise CommandResolvingError(dto, '\n'.join(errors))
