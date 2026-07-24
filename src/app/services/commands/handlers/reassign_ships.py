from typing import Optional

from pydantic import Field

from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.reassign_ships import ReassignShipsCommand, ShipReassignOp


class ReassignShipsCommandParams(FleetCommand):
    target_fleet_id: Optional[int] = None
    operations: list[ShipReassignOp] = Field(min_length=1)


def reassign_ships_command(world: World, params: ReassignShipsCommandParams):
    fleet = world.find_fleet(params.fleet_id)

    if fleet is None:
        return

    fleet.command_queue.add(
        ReassignShipsCommand(params.target_fleet_id, params.operations),
        params.on_top,
    )
