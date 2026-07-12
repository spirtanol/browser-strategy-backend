from typing import Literal

from .base import FleetTargeted
from app.entities.world import World


class CancelCommandParams(FleetTargeted):
    scope: Literal['current', 'last', 'all'] = 'all'

def cancel_command(world: World, params: CancelCommandParams):
    fleet = world.find_fleet(params.fleet_id)
    
    if fleet is None:
        return

    match params.scope:
        case 'current':
            fleet.command_queue.pop_current()
        case 'last':
            fleet.command_queue.pop_last()
        case 'all':
            fleet.command_queue.cancel_all()
