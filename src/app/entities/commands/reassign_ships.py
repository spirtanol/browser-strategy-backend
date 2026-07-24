from __future__ import annotations
from typing import TypedDict, Optional, Any, TYPE_CHECKING

import app.defs.consts as Consts
from app.defs.enums import ObjectType, MovingState, ShipReassignOpType
from app.utils import xy
from .base import BaseCommand
from .factory import register_command
from .move_to_object import MoveToObjectCommand

if TYPE_CHECKING:
    from ..fleet import FleetEntity


class ShipReassignOp(TypedDict):
    ship_id: int
    op: ShipReassignOpType


@register_command()
class ReassignShipsCommand(BaseCommand):
    name = 'reassign_ships'

    def __init__(
        self,
        target_fleet_id: Optional[int] = None,
        operations: Optional[list[ShipReassignOp]] = None,
    ):
        super().__init__()
        self.target_fleet_id = target_fleet_id
        self.operations = operations if operations is not None else []
        self.stage = 0
        self.is_process = False
        if not self.operations:
            self.finished = True

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['target_fleet_id'] = self.target_fleet_id
        data['operations'] = self.operations
        data['stage'] = self.stage
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.target_fleet_id = data.get('target_fleet_id')
        self.operations = data.get('operations', [])
        self.stage = data.get('stage', 0)

    def update(self, dt: float):
        if self.finished or self.is_process:
            return

        if self.target_fleet_id is None:
            self._start_apply_split()
            return

        match self.stage:
            case 0:
                target = self.world.find_fleet(self.target_fleet_id)
                if target is None:
                    self.finished = True
                    return

                distance = xy.distance(
                    self.fleet.pos.x,
                    self.fleet.pos.y,
                    target.pos.x,
                    target.pos.y,
                )
                if distance > Consts.ObjectRadius:
                    move_command = MoveToObjectCommand(
                        self.target_fleet_id,
                        ObjectType.Fleet,
                    )
                    move_command.is_dependent = True
                    self.queue.add(move_command, True)
                else:
                    self.stage = 1
            case 1:
                target = self.world.find_fleet(self.target_fleet_id)
                if target is None:
                    self.finished = True
                    return

                if target.moving_state not in (MovingState.Idle, MovingState.Docked):
                    self.finished = True
                    return

                self._start_apply_transfer(target)

    def _start_apply_split(self):
        async def apply():
            fleet_a = self.fleet
            new_fleet = await self.world.create_fleet(
                fleet_a.owner_id, fleet_a.pos.x, fleet_a.pos.y
            )

            for op in self.operations:
                if op['op'] != ShipReassignOpType.Detach:
                    continue
                ship = fleet_a.ships.get(op['ship_id'])
                if ship is None:
                    continue
                fleet_a.remove_ship(ship)
                new_fleet.add_ship(ship)

            if not fleet_a.ships:
                self.world.remove_fleet(fleet_a)

            self.finished = True

        self.world.add_async_action(apply)
        self.is_process = True

    def _start_apply_transfer(self, target: FleetEntity):
        async def apply():
            fleet_a = self.fleet
            fleet_b = self.world.find_fleet(target.id)
            if fleet_b is None or fleet_b.owner_id != fleet_a.owner_id:
                self.finished = True
                return

            for op in self.operations:
                if op['op'] == ShipReassignOpType.Detach:
                    ship = fleet_a.ships.get(op['ship_id'])
                    if ship is None:
                        continue
                    fleet_a.remove_ship(ship)
                    fleet_b.add_ship(ship)
                elif op['op'] == ShipReassignOpType.Attach:
                    ship = fleet_b.ships.get(op['ship_id'])
                    if ship is None:
                        continue
                    fleet_b.remove_ship(ship)
                    fleet_a.add_ship(ship)

            if not fleet_a.ships:
                self.world.remove_fleet(fleet_a)
            if not fleet_b.ships:
                self.world.remove_fleet(fleet_b)

            self.finished = True

        self.world.add_async_action(apply)
        self.is_process = True
