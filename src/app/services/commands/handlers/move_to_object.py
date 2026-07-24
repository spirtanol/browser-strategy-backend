from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.move_to_object import MoveToObjectCommand
from app.defs.enums import ObjectType


class MoveToObjectCommandParams(FleetCommand):
    obj_id: int
    obj_type: ObjectType


def move_to_object_command(world: World, params: MoveToObjectCommandParams):
    fleet = world.find_fleet(params.fleet_id)

    if fleet is None:
        return

    match params.obj_type:
        case ObjectType.Platform:
            if world.find_platform(params.obj_id) is None:
                return
        case ObjectType.Site:
            if world.find_site(params.obj_id) is None:
                return
        case ObjectType.Fleet:
            if world.find_fleet(params.obj_id) is None:
                return
        case _:
            return

    if params.clear_queue:
        fleet.command_queue.cancel_all()

    fleet.command_queue.add(
        MoveToObjectCommand(obj_id=params.obj_id, obj_type=params.obj_type),
        params.on_top,
    )
