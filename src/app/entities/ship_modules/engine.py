from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .base import BaseShipModule, UpdatePhase
from app.defs.modules import EngineModuleDef, BaseEngine
from app.defs.items import NetworkResource, MDO
from .factory import register_module
from app.defs.enums import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity


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
                thrust = self.__def.thrust * self.efficiency if self.fuel > 0 else 0
                self.ship.storage.get_net(NetworkResource.Thrust).add(self.id, thrust)
            elif phase == UpdatePhase.Execution:
                state = self.ship.fleet.moving_state
                if state in (MovingState.Move, MovingState.Maneuvering, MovingState.Fishing):
                    damage = self.max_hp * self.__def.wear_per_hour * (dt / 3600.0)
                    self.hp = self.hp - damage

                consumption = 0
                if state == MovingState.Move:
                    consumption = self.__def.fuel_consumption * dt / 3600.0
                elif state in (MovingState.Maneuvering, MovingState.Fishing):
                    consumption = self.__def.fuel_consumption * dt / 7200.0
                    
                if self.fuel <= consumption or self.fuel <= 0:
                    have, write_off = self.ship.request_item(MDO, self.__def.fuel_consumption)
                    self.fuel += have
                    write_off()
                    
                    self.fuel -= min(consumption, self.fuel)
                    self.ship.storage.get_net(NetworkResource.Weight).add(self.id, self.fuel * MDO.weight)

    def on_attached(self, ship: ShipEntity):
        self.update(0.0, UpdatePhase.Anounce)