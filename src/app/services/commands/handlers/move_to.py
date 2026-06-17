from .base import ShipCommand
from app.entities.world import World
from app.entities.commands.move import MoveCommand


class MoveToCommandParams(ShipCommand):
    x: float
    y: float

def move_to_command(world: World, params: MoveToCommandParams):
    ship = world.find_ship(params.ship_id)
    
    if ship is None:
        return

    if params.clear_queue:
        ship.command_queue.clear()
    ship.command_queue.add(MoveCommand(params.x, params.y), params.on_top)