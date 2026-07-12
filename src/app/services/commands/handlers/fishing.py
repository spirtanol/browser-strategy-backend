from pydantic import Field

from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.fishing import FishingCommand, FillLimit


class FishingCommandParams(FleetCommand):
    site_id: int
    fill_limmits: list[FillLimit] = Field(min_length=1)

def fishing_command(world: World, params: FishingCommandParams):
    fleet = world.find_fleet(params.fleet_id)

    if fleet is None:
        return

    site = world.find_site(params.site_id)

    if site is None:
        return

    if params.clear_queue:
        fleet.command_queue.cancel_all()
    
    fleet.command_queue.add(FishingCommand(site_id=params.site_id, target_quantity=params.target_quantity), params.on_top)
