from typing import Optional

from pydantic import Field

from .base import FleetCommand
from app.entities.world import World
from app.entities.commands.transfer_cargo import TransferCargoCommand, TransferOperation


class TransferCargoCommandParams(FleetCommand):
    target_fleet_id: Optional[int] = None
    operations: list[TransferOperation] = Field(min_length=1)


def transfer_cargo_command(world: World, params: TransferCargoCommandParams):
    fleet = world.find_fleet(params.fleet_id)

    if fleet is None:
        return

    if params.clear_queue:
        fleet.command_queue.cancel_all()

    fleet.command_queue.add(
        TransferCargoCommand(
            target_fleet_id=params.target_fleet_id,
            operations=params.operations,
        ),
        params.on_top,
    )
