from __future__ import annotations
from typing import Optional, TypeVar, TYPE_CHECKING
import enum

from app.defs.modules import ModuleDef
from app.entities.resources_pool import ResourcesPool
from app.defs.items import NetworkResource
from app.defs.enums import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity


T = TypeVar('T', bound='BaseShipModule')

class UpdatePhase(enum.IntEnum):
    Anounce = 1
    Balance = 2
    Execution = 3

class BaseShipModule:
    def __init__(
        self, 
        module_def: ModuleDef,
        id: int,
    ):
        self.id = id
        self.module_def = module_def
        self._hp = module_def.hp
        self.ship: Optional[ShipEntity] = None

    def to_dict(self) -> dict[str, any]:
        return {
            'id': self.id,
            'hp': self._hp
        }

    @classmethod
    def from_dict(cls, module_def: ModuleDef, data: dict) -> T:
        instance = cls(module_def, 0)
        instance.load_state(data)
        return instance

    def load_state(self, state: dict[str, any]):
        self.id = state.get('id', 0)
        self._hp = state.get('hp', self.module_def.hp)

    def update(self, dt: float, phase: UpdatePhase):
        pass

    def attached(self, ship: ShipEntity):
        self.ship = ship
        self.ship.get_net(NetworkResource.Weight).add(self.id, self.module_def.weight)
        self.ship.get_net(NetworkResource.HP).add(self.id, self.module_def.hp)
        self.ship_moving_state_changed(MovingState.Idle, ship.moving_state)
        self.on_attached(ship)

    def detached(self):
        if self.ship:
            for res in NetworkResource:
                self.ship.get_net(res).remove(self.id)
            self.on_detached()
            self.ship = None

    def on_attached(self, ship: ShipEntity):
        pass

    def on_detached(self):
        pass

    def ship_moving_state_changed(self, old_state: MovingState, new_state: MovingState):
        pass