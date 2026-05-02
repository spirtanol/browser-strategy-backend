from .base import BaseModuleEntity, UpdatePhase
from app.defs.items import NetworkResource, FUEL_BARREL, EMPTY_BARREL
from app.defs.modules import GeneratorModuleDef


CYCLE_DURATION = 24.0 * 60.0 * 60.0
FUEL_WEIGHT = FUEL_BARREL.weight - EMPTY_BARREL.weight

class GeneratorModuleEntity(BaseModuleEntity):
    def __init__(self,  module_def: GeneratorModuleDef):
        super().__init__(module_def)
        self.fuel: float = 0.0
        self.active: bool = True

    def to_dict(self) -> dict:
        data = super().to_dict()
        data['fuel'] = self.fuel
        data['active'] = self.active
        return data

    def from_dict(self, data: dict):
        super().from_dict(data)
        self.fuel = data.get('fuel', 0.0)
        self.active = data.get('active', True)

    def update(self, dt: float, phase: UpdatePhase):
        if self.active:
            if phase == UpdatePhase.Anounce:
                output = self.module_def.output if self.fuel > 0 else 0.0
                self.env.get_suppliers(NetworkResource.Power).add_pool(self.id, output)
                self.env.get_suppliers(NetworkResource.Weight).add_pool(self.id, self.fuel * FUEL_WEIGHT)
            elif phase == UpdatePhase.Execution:
                consumption = min(dt / CYCLE_DURATION, 1.0)
                if self.fuel <= consumption:
                    if self.env.pull(FUEL_BARREL, 1):
                        self.env.push(EMPTY_BARREL, 1)
                        self.fuel += 1.0
                self.fuel -= min(consumption, self.fuel)
                