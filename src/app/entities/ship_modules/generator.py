from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseShipModule, UpdatePhase
from app.defs.items import NetworkResource, FUEL_BARREL, EMPTY_BARREL
from app.defs.modules import GeneratorModuleDef, BaseGenerator
from .factory import register_module
from app.defs.consts import DayLenght

if TYPE_CHECKING:
    from ..ship import ShipEntity


FUEL_WEIGHT = FUEL_BARREL.weight - EMPTY_BARREL.weight

@register_module(BaseGenerator.name)
class GeneratorModule(BaseShipModule):
    def __init__(
        self,  
        module_def: GeneratorModuleDef,
        id: int,
        active: bool = True
    ):
        super().__init__(module_def, id)
        self.fuel: float = 0.0
        self.active: bool = active
        self.__def = module_def

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['fuel'] = self.fuel
        data['active'] = self.active
        return data

    def load_state(self, data: dict[str, any]):
        super().load_state(data)
        self.fuel = data.get('fuel', 0.0)
        self.active = data.get('active', True)

    def update(self, dt: float, phase: UpdatePhase):
        if self.active:
            if phase == UpdatePhase.Anounce:
                output = self.module_def.output if self.fuel > 0 else 0.0
                self.ship.get_net(NetworkResource.PowerOut).add(self.id, output)
                self.ship.get_net(NetworkResource.Weight).add(self.id, self.fuel * FUEL_WEIGHT)
            elif phase == UpdatePhase.Execution:
                consumption = dt / DayLenght * self.__def.fuel_consumption
                if self.fuel <= consumption:
                    if self.ship.pull(FUEL_BARREL, 1):
                        self.ship.push(EMPTY_BARREL, 1)
                        self.fuel += 1.0
                self.fuel -= min(consumption, self.fuel)
    
    def on_attached(self, ship: ShipEntity):
        self.update(0.0, UpdatePhase.Anounce)