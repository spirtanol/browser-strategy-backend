from pydantic import BaseModel

from .base import ShipCommand
from app.entities.world import World
from app.entities.commands.move_to_object import MoveToObjectCommand
from app.core.types import ObjectType


class MoveToObjectCommandParams(ShipCommand):
    obj_id: int
    obj_type: ObjectType

def move_to_object_command(world: World, params: MoveToObjectCommandParams):
    ship = world.find_ship(params.ship_id)

    if ship is None:
        return

    x = None
    y = None

    match params.obj_type:
        case ObjectType.Platform:
            platform = world.find_platform(params.obj_id)

            if platform is None:
                return
        case _:
            return

    if params.clear_queue:
        ship.command_queue.clear()
        
    ship.command_queue.add(MoveToObjectCommand(obj_id=params.obj_id, obj_type=params.obj_type), params.on_top)