from __future__ import annotations
from typing import Optional, override, TYPE_CHECKING
import math
import enum

from .base import MapEntity
from app.utils.str_helpers import generate_random_string
from .commands.command_queue import CommandQueue
from .world import World
from app.utils import xy
from app.defs.enums import MovingState, ObjectType
from .anchor_point import AnchorPointEntity
from app.defs.items import NetworkResource

if TYPE_CHECKING:
    from .ship import ShipEntity


class FleetEntity(MapEntity):
    def __init__(self, id: int = 0, name: str = ''):
        super().__init__()
        self.owner_id: int = 0
        self.name: str = name
        self.pos = xy.Position()
        self.command_queue = CommandQueue(self)
        self._move_state: MovingState = MovingState.Idle
        self.attached_to_id: Optional[int] = None
        self.attached_to_type: Optional[ObjectType] = None
        self.ships: dict[int, ShipEntity] = {}

    @property
    def moving_state(self) -> MovingState:
        return self._move_state

    @moving_state.setter
    def moving_state(self, new_state: MovingState) -> None:
        if new_state == self._move_state:
            return
        
        old_state = self._move_state
        self._move_state = new_state
        for ship in self.ships.values():
            ship.moving_state_changed(old_state, new_state)

    def update(self, dt: float):
        for ship in self.ships.values():
            ship.update(dt)
        self.command_queue.update(dt)

    @property
    def max_speed(self) -> float:
        speed = 9999
        for ship in self.ships.values():
            speed = min(speed, ship.max_speed)
        return speed

    def add_ship(self, ship: ShipEntity):
        self.ships[ship.id] = ship
        ship.fleet_id = self.id
        ship.moving_state_changed(MovingState.Idle, self.moving_state)

    def remove_ship(self, ship: ShipEntity):
        self.ships.pop(ship.id, None)
        ship.fleet_id = 0

    def attach_to(self, anchor_point: AnchorPointEntity) -> None:
        self.attached_to_id = anchor_point.get_id()
        self.attached_to_type = anchor_point.get_type()
        anchor_point.attach(self.id)

    def detach(self, anchor_point: AnchorPointEntity) -> None:
        if self.attached_to_id is None:
            return
        
        self.attached_to_id = None
        self.attached_to_type = None
        anchor_point.detach(self.id)

    def get_net_value(self, resource: NetworkResource) -> int | float:
        value = 0
        for ship in self.ships.values():
            value += ship.get_net(resource).value
        return value

    @override
    def get_type(self) -> ObjectType:
        return ObjectType.Fleet
