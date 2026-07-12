from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.docking import DockingCommand


class DockToPlatformCommandParams(FleetCommand):
    platform_id: int

def dock_to_platform_command(world: World, params: DockToPlatformCommandParams):
    fleet = world.find_fleet(params.fleet_id)

    if fleet is None:
        return

    x = None
    y = None

    platform = world.find_platform(params.platform_id)
    if platform is None:
        return

    if params.clear_queue:
        fleet.command_queue.cancel_all()
        
    fleet.command_queue.add(DockingCommand(platform_id=params.platform_id), params.on_top)