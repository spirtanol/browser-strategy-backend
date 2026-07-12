from pydantic import Field

from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.trade import TradeOperation, TradeCommand
from .dock_to_platform import DockToPlatformCommandParams


class TradeCommandParams(DockToPlatformCommandParams):
    operations: list[TradeOperation] = Field(min_length=1)

def trade_command(world: World, params: TradeCommandParams):
    fleet = world.find_fleet(params.fleet_id)
    
    if fleet is None:
        return

    if params.clear_queue:
        fleet.command_queue.cancel_all()

    fleet.command_queue.add(TradeCommand(params.platform_id, params.operations), params.on_top)