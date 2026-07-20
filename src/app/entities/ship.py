from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Callable
import math

from .storage import Storage, StorageItemType
from .resources_pool import ResourcesPool
from app.defs.items import MEAL, NetworkResource
from .ship_modules.base import BaseShipModule, UpdatePhase
from .ship_modules import factory as ModuleFactory
from app.utils.str_helpers import generate_random_string
from app.defs.enums import MovingState
from app.defs.consts import HungerCycle, EnvironmentSpeedFactor
from .ship_hull import ShipHull

if TYPE_CHECKING:
    from .fleet import FleetEntity


class ShipEntity:
    def __init__(self, id: int = 0, name: str = ''):
        self.id: int = id
        self.fleet_id: int = 0
        self.fleet: Optional[FleetEntity] = None
        self.counter: int = 0
        self.storage = Storage()
        self.crew: int = 0
        self.hunger: float = 0.0
        self.name: str = name
        self.modules: list[BaseShipModule] = []
        self.hull = ShipHull()
        self._locked_in_slots: int = 0
        self._locked_ex_slots: int = 0

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def update(self, dt: float):
        self._crew_update(dt)
        self._modules_update(dt)

    def _modules_update(self, dt: float):
        for phase in (UpdatePhase.Anounce, UpdatePhase.Balance, UpdatePhase.Execution):
            for module in self.modules:
                module.update(dt, phase)

    def _crew_update(self, dt: float):
        if self.crew <= 0:
            return

        self.hunger += (dt / HungerCycle)

        if self.hunger >= 1.0:
            have, write_off = self.request_item(MEAL, self.crew)
            if have > 0:
                self.hunger -= have / self.crew
                write_off()
                
    def request_item(self, item_type: StorageItemType, amount: int) -> tuple[int, Callable]:
        have = self.storage.get_amount(item_type)
        if have >= amount:
            def write_off():
                self.storage.pull(item_type, amount)
            return (amount, write_off)
        
        left = amount - have
        fleet_have, fleet_write_off = self.fleet.request_item(self, item_type, left)
        def write_off():
            self.storage.pull(item_type, have)
            fleet_write_off()
        return (have + fleet_have, write_off)
        
    def add_module(self, module: BaseShipModule):
        self.modules.append(module)
        module.attached(self)
        self._locked_in_slots += module.in_slots
        self._locked_ex_slots += module.ex_slots

    def remove_module(self, module: BaseShipModule):
        self.modules.remove(module)
        self._locked_in_slots -= module.in_slots
        self._locked_ex_slots -= module.ex_slots
        module.detached()

    @property
    def in_slots(self) -> int:
        return self._locked_in_slots

    @property
    def ex_slots(self) -> int:
        return self._locked_ex_slots

    @property
    def weight(self) -> float:
        weight = self.storage.get_total_mass()
        weight += self.storage.get_net(NetworkResource.Weight).value
        return weight + self.hull.get_weight()

    @property
    def hp(self) -> int:
        return self.storage.get_net(NetworkResource.HP).value + self.hull.get_health()

    @property
    def floatage(self) -> int:
        return self.hull.get_floatage()

    @property
    def volume(self) -> float:
        return self.storage.get_total_volume()

    @property
    def max_volume(self) -> float:
        return self.hull.get_volume(self.in_slots, self.ex_slots)

    @property
    def max_speed(self) -> float:
        thrust = self.storage.get_net(NetworkResource.Thrust).value
        base_drag = math.sqrt(self.floatage)
    
        load_ratio = self.weight / self.floatage
        
        speed = (thrust / base_drag) * (1.0 - (load_ratio * 0.3)) * EnvironmentSpeedFactor
        return speed

    def moving_state_changed(self, old_state: MovingState, new_state: MovingState):
        for module in self.modules:
            module.ship_moving_state_changed(old_state, new_state)