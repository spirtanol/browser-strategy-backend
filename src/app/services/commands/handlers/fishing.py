from .base import ShipCommand
from app.entities.world import World
from app.entities.commands.fishing import FishingCommand


class FishingCommandParams(ShipCommand):
    site_id: int
    target_quantity: int

def fishing_command(world: World, params: FishingCommandParams):
    ship = world.find_ship(params.ship_id)

    if ship is None:
        return

    site = world.find_site(params.site_id)

    if site is None:
        return

    if params.clear_queue:
        ship.command_queue.cancel_all()
    
    ship.command_queue.add(FishingCommand(site_id=params.site_id, target_quantity=params.target_quantity), params.on_top)
