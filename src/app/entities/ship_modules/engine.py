from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .base import BaseShipModule, UpdatePhase
from app.defs.modules import EngineModuleDef, BaseEngine
from app.defs.items import FUEL_BARREL, EMPTY_BARREL, NetworkResource
from .factory import register_module
from app.defs.enums import MovingState
from app.defs.consts import DayLenght

if TYPE_CHECKING:
    from ..ship import ShipEntity


FUEL_WEIGHT = FUEL_BARREL.weight - EMPTY_BARREL.weight

@register_module(BaseEngine.name)
class EngineModule(BaseShipModule):
    def __init__(
        self,  
        module_def: EngineModuleDef,
        id: int,
        active: bool = True
    ):
        super().__init__(module_def, id)
        self.__def = module_def
        self.fuel: float = 0.0
        self.active: bool = active

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['fuel'] = self.fuel
        data['active'] = self.active
        return data

    def load_state(self, data: dict[str, Any]):
        super().load_state(data)
        self.fuel = data.get('fuel', 0.0)
        self.active = data.get('active', True)

    def update(self, dt: float, phase: UpdatePhase):
        if self.ship is None:
            return

        if self.active:
            if phase == UpdatePhase.Anounce:
                thrust = self.module_def.thrust
                self.ship.get_net(NetworkResource.Thrust).add(self.id, thrust)
            elif phase == UpdatePhase.Execution:
                cdt = dt / DayLenght
                consumption = 0
                if self.ship.moving_state == MovingState.Move:
                    consumption = cdt * self.__def.fuel_consumption
                elif self.ship.moving_state in (MovingState.Maneuvering, MovingState.Fishing):
                    consumption = cdt * self.__def.fuel_consumption * 0.5
                    
                if consumption > 0:
                    if self.fuel <= consumption:
                        if self.ship.pull(FUEL_BARREL, 1):
                            self.ship.push(EMPTY_BARREL, 1)
                            self.fuel += 1.0
                    self.fuel -= min(consumption, self.fuel)
                    self.ship.get_net(NetworkResource.Weight).add(self.id, self.fuel * FUEL_WEIGHT)

    def on_attached(self, ship: ShipEntity):
        self.update(0.0, UpdatePhase.Anounce)