from .base import ShipCommand
from app.entities.world import World
from app.entities.commands.trade import TradeOperation, TradeCommand
from .dock_to_platform import DockToPlatformCommandParams


class TradeCommandParams(DockToPlatformCommandParams):
    operations: list[TradeOperation]

def trade_command(world: World, params: TradeCommandParams):
    ship = world.find_ship(params.ship_id)
    
    if ship is None:
        return

    if params.clear_queue:
        ship.command_queue.clear()

    ship.command_queue.add(TradeCommand(params.platform_id, params.operations), params.on_top)