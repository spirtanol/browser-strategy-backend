from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseShipModule, UpdatePhase
from app.defs.modules import BaseEngine, HarvesterModuleDef
from app.defs.enums import MovingState
from app.defs.items import NetworkResource, Fish

if TYPE_CHECKING:
    from ..ship import ShipEntity
    from ..world import World


class FishNetModule(BaseShipModule):
    def __init__(
        self,
        module_def: HarvesterModuleDef,
        id: int,
        active: bool = True
    ):
        super().__init__(module_def, env, id)
        self.__def = module_def
        self.active: bool = active

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['active'] = self.active
        return data
    
    def load_state(self, data: dict[str, any]):
        super().load_state(data)
        self.active = data.get('active', True)

    def update(self, dt: float, phase: UpdatePhase):
        pass

    def ship_moving_state_changed(self, old_state: MovingState, new_state: MovingState):
        if new_state == MovingState.Fishing:
            self.ship.get_net(NetworkResource.PowerIn).add(self.id, self.__def.energy_consumption)
        else:
            self.ship.get_net(NetworkResource.PowerIn).remove(self.id)

    def on_attached(self, ship: ShipEntity):
        self.ship.get_net(NetworkResource.HarvestingFish).add(self.id, self.__def.harvest_power)

    def on_detached(self):
        self.ship.get_net(NetworkResource.HarvestingFish).remove(self.id)