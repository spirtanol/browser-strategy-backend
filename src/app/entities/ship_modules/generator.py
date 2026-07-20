from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .base import BaseShipModule, UpdatePhase
from app.defs.items import NetworkResource, MDO
from app.defs.modules import GeneratorModuleDef, BaseGenerator
from .factory import register_module

if TYPE_CHECKING:
    from ..ship import ShipEntity


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
        if self.active:
            if phase == UpdatePhase.Anounce:
                output = self.module_def.output if self.fuel > 0 else 0.0
                self.ship.storage.get_net(NetworkResource.PowerOut).add(self.id, output)
                self.ship.storage.get_net(NetworkResource.Weight).add(self.id, self.fuel * MDO.weight)
            elif phase == UpdatePhase.Execution:
                consumption = dt / 3600.0 * self.__def.fuel_consumption
                if self.fuel <= consumption:
                    have, write_off = self.ship.request_item(MDO, self.__def.fuel_consumption)
                    self.fuel += have
                    write_off()

                self.fuel -= min(consumption, self.fuel)
    
    def on_attached(self, ship: ShipEntity):
        self.update(0.0, UpdatePhase.Anounce)