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
        self._progress: float = 0.0

    def to_dict(self) -> dict[str, any]:
        data = super().to_dict()
        data['active'] = self.active
        data['progress'] = self._progress
        return data
    
    def load_state(self, data: dict[str, any]):
        super().load_state(data)
        self.active = data.get('active', True)
        self._progress = data.get('progress', 0.0)

    def update(self, dt: float, phase: UpdatePhase, world: World):
        if self.ship.moving_state == MovingState.Fishing:
            self._progress += dt
            if self._progress >= self.__def.cycle:
                self._progress -= self.__def.cycle
                site = world.find_site(self.ship.attached_to_id)
                extraction_quantity = self.__def.harvest_power * site.efficiency
                site.reserve -= extraction_quantity
                fish_quantity = int(extraction_quantity * 1000 / Fish.weight)
                self.ship.storage.push(Fish, fish_quantity)


    def ship_moving_state_changed(self, old_state: MovingState, new_state: MovingState):
        if new_state == MovingState.Fishing:
            self.ship.get_net(NetworkResource.PowerIn).add(self.id, self.__def.energy_consumption)
        else:
            self.ship.get_net(NetworkResource.PowerIn).remove(self.id)
        self._progress: float = 0.0