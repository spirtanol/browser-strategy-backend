from typing import Literal

from .base import ShipTargeted
from app.entities.world import World


class CancelCommandParams(ShipTargeted):
    scope: Literal['current', 'last', 'all'] = 'all'

def cancel_command(world: World, params: CancelCommandParams):
    ship = world.find_ship(params.ship_id)
    
    if ship is None:
        return

    match params.scope:
        case 'current':
            ship.command_queue.pop_current()
        case 'last':
            ship.command_queue.pop_last()
        case 'all':
            ship.command_queue.cancel_all()
