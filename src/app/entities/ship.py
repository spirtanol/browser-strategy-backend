from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Callable
import math

from .storage import Storage, StorageItemType
from app.defs.items import MEAL, WeldingKit, NetworkResource
from .ship_modules.base import BaseShipModule, UpdatePhase
from app.defs.enums import MovingState
from app.defs.consts import (
    HungerCycle, 
    EnvironmentSpeedFactor, 
    RepairPerCrewMember, 
    RepairCycle, 
    WeldingKitHp, 
    HungerThreshold
)
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
        self.hull_hp: float = 0.0
        self.repair_buffer: float = 0.0

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def update(self, dt: float):
        self._crew_update(dt)
        self._hull_wear_update(dt)
        self._repair_update(dt)
        self._modules_update(dt)

    def _modules_update(self, dt: float):
        for phase in (UpdatePhase.Anounce, UpdatePhase.Balance, UpdatePhase.Execution):
            for module in self.modules:
                module.update(dt, phase)

    def _hull_wear_update(self, dt: float):
        if self.fleet.moving_state not in (MovingState.Move, MovingState.Maneuvering, MovingState.Fishing):
            return
        max_hp = self.hull.get_max_health()
        damage = max_hp * self.hull.hull_config.wear_per_hour * (dt / 3600.0)
        self.hull_hp = max(0.0, self.hull_hp - damage)

    def _crew_update(self, dt: float):
        if self.crew <= 0:
            return

        self.hunger += (dt / HungerCycle)

        if self.hunger >= 1.0:
            have, write_off = self.request_item(MEAL, self.crew)
            if have > 0:
                self.hunger -= have / self.crew
                write_off()
            elif self.hunger >= HungerThreshold:
                self.crew -= 1
                if self.crew <= 0:
                    self.hunger = 0.0
                    return
                self.hunger = 1.0

    def _needs_repair(self) -> bool:
        if self.hull_hp < self.hull.get_max_health():
            return True
        return any(m.hp < m.max_hp for m in self.modules)

    def _repair_update(self, dt: float):
        surplus = max(0.0, self.work_out - self.storage.get_net(NetworkResource.WorkIn).value)
        if surplus <= 0:
            return
        if self.fleet.moving_state not in (MovingState.Idle, MovingState.Docked):
            return

        if not self._needs_repair():
            return

        if self.repair_buffer <= 0:
            have, write_off = self.request_item(WeldingKit, 1)
            if have < 1:
                return
            write_off()
            self.repair_buffer = 1.0

        points = surplus * RepairPerCrewMember * (dt / RepairCycle)
        if points <= 0:
            return

        points = min(points, self.repair_buffer * WeldingKitHp)
        self._apply_repair(points)
        self.repair_buffer -= points / WeldingKitHp

    def _apply_repair(self, points: float):
        damaged_modules = [m for m in self.modules if m.hp < m.max_hp]
        hull_damaged = self.hull_hp < self.hull.get_max_health()
        n = len(damaged_modules) + (1 if hull_damaged else 0)
        if n == 0:
            return

        share = points / n
        for module in damaged_modules:
            module.hp = module.hp + share
        if hull_damaged:
            self.hull_hp = min(self.hull_hp + share, float(self.hull.get_max_health()))
                
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
    def work_out(self) -> float:
        return float(self.crew)

    @property
    def work_efficiency(self) -> float:
        work_in = self.storage.get_net(NetworkResource.WorkIn).value
        if work_in <= 0:
            return 1.0
        return min(self.work_out / work_in, 1.0)

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
        return int(self.storage.get_net(NetworkResource.HP).value + self.hull_hp)

    @property
    def max_hp(self) -> int:
        return int(sum(module.max_hp for module in self.modules) + self.hull.get_max_health())

    @property
    def floatage(self) -> float:
        return self.hull.get_floatage()

    @property
    def volume(self) -> float:
        return self.storage.get_total_volume()

    @property
    def max_volume(self) -> float:
        return self.hull.get_volume(self.in_slots, self.ex_slots)

    def fit_quantity(self, item_type: StorageItemType, quantity: int) -> int:
        if quantity <= 0:
            return 0
        free_volume = self.max_volume - self.volume
        if free_volume < item_type.volume * quantity:
            quantity = int(free_volume / item_type.volume)
        free_floatage = self.floatage - self.weight
        if free_floatage < item_type.weight * quantity:
            quantity = int(free_floatage / item_type.weight)
        return max(quantity, 0)

    @property
    def max_speed(self) -> float:
        thrust = self.storage.get_net(NetworkResource.Thrust).value
        base_drag = math.sqrt(self.floatage)
    
        load_ratio = self.weight / self.floatage
        
        speed = (thrust / base_drag) * (1.0 - (load_ratio * 0.3)) * EnvironmentSpeedFactor
        max_hull = self.hull.get_max_health()
        hull_condition = (self.hull_hp / max_hull) if max_hull > 0 else 0.0
        return speed * (0.5 + 0.5 * hull_condition)

    def moving_state_changed(self, old_state: MovingState, new_state: MovingState):
        for module in self.modules:
            module.ship_moving_state_changed(old_state, new_state)

    def on_resource_extracted(self, fraction: float):
        for module in self.modules:
            module.on_resource_extracted(fraction)