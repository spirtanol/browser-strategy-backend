from .base import BaseModule, UpdatePhase, Environment
from app.defs.items import NetworkResource, FUEL_BARREL, EMPTY_BARREL
from app.defs.modules import GeneratorModuleDef, GENERATOR
from .factory import register_module


CYCLE_DURATION = 24.0 * 60.0 * 60.0
FUEL_WEIGHT = FUEL_BARREL.weight - EMPTY_BARREL.weight

@register_module(GENERATOR.name)
class GeneratorModule(BaseModule):
    def __init__(
        self,  
        module_def: GeneratorModuleDef,
        env: Environment,
        id: int,
        active: bool = True
    ):
        super().__init__(module_def, env, id)
        self.fuel: float = 0.0
        self.active: bool = active

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
                self.env.get_net(NetworkResource.PowerOut).add(self.id, output)
                self.env.get_net(NetworkResource.Weight).add(self.id, self.fuel * FUEL_WEIGHT)
            elif phase == UpdatePhase.Execution:
                consumption = min(dt / CYCLE_DURATION, 1.0)
                if self.fuel <= consumption:
                    if self.env.pull(FUEL_BARREL, 1):
                        self.env.push(EMPTY_BARREL, 1)
                        self.fuel += 1.0
                self.fuel -= min(consumption, self.fuel)
    
    def onAttached(self, env: Environment):
        self.update(0.0, UpdatePhase.Anounce)