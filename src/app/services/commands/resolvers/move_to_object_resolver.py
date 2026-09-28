from .base import ResolverContext, CommandResolvingError
from app.entities.player import PlayerEntity
from ..handlers.move_to_object import MoveToObjectCommandParams, ObjectType
from .fleet_resolver import fleet_command_resolver


async def move_to_object_resolver(context: ResolverContext, player: PlayerEntity, dto: MoveToObjectCommandParams):
    await fleet_command_resolver(context, player, dto)

    match dto.obj_type:
        case ObjectType.Platform:
            platform = await context.client_platform_service.find(dto.obj_id)
            if platform is None:
                raise CommandResolvingError(dto, f'Платформа {dto.obj_id} не существует')
            if platform.owner_id == player.id:
                return
        case ObjectType.Site:
            if not await context.client_site_service.exists(dto.obj_id):
                raise CommandResolvingError(dto, f'Сайт {dto.obj_id} не существует')
        case ObjectType.Fleet:
            if dto.obj_id == dto.fleet_id:
                raise CommandResolvingError(dto, f'Флот {dto.fleet_id} не может двигаться к себе')
            fleet = await context.client_fleet_service.find(dto.obj_id)
            if fleet is None:
                raise CommandResolvingError(dto, f'Флот {dto.obj_id} не существует')
            if fleet.owner_id == player.id:
                return
        case _:
            raise CommandResolvingError(dto, f'Объект {dto.obj_type}:{dto.obj_id} не существует')

    player_map = await context.client_player_service.get_cached_map(player.id)
    known = {
        ObjectType.Platform: player_map.platforms if player_map is not None else set(),
        ObjectType.Site: player_map.sites if player_map is not None else set(),
        ObjectType.Fleet: player_map.fleets if player_map is not None else set(),
    }
    if dto.obj_id in known[dto.obj_type]:
        return

    raise CommandResolvingError(dto, f'Объект {dto.obj_type}:{dto.obj_id} неизвестен')
