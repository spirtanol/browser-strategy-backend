from pydantic import BaseModel

from .base import ShipCommand
from app.entities.world import World
from app.entities.commands.docking import DockingCommand


class DockToPlatformCommandParams(ShipCommand):
    platform_id: int

def dock_to_platform_command(world: World, params: DockToPlatformCommandParams):
    ship = world.find_ship(params.ship_id)

    if ship is None:
        return

    x = None
    y = None

    platform = world.find_platform(params.platform_id)
    if platform is None:
        return

    if params.clear_queue:
        ship.command_queue.clear()
        
    ship.command_queue.add(DockingCommand(platform_id=params.platform_id), params.on_top)