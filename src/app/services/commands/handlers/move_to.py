from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.move import MoveCommand


class MoveToCommandParams(FleetCommand):
    x: float
    y: float

def move_to_command(world: World, params: MoveToCommandParams):
    fleet = world.find_fleet(params.fleet_id)
    
    if fleet is None:
        return

    if params.clear_queue:
        fleet.command_queue.cancel_all()
    fleet.command_queue.add(MoveCommand(params.x, params.y), params.on_top)