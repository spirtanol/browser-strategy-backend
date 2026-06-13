from .base import BaseModule, UpdatePhase
from app.entities.environment import MovableEnvironment, Environment
from app.defs.modules import EngineModuleDef, ENGINE
from app.defs.items import FUEL_BARREL, EMPTY_BARREL, NetworkResource
from .factory import register_module
from app.core.types import MovingState


CYCLE_DURATION = 4.0 * 60.0 * 60.0
FUEL_WEIGHT = FUEL_BARREL.weight - EMPTY_BARREL.weight

@register_module(ENGINE.name)
class EngineModule(BaseModule):
    def __init__(
        self,  
        module_def: EngineModuleDef,
        env: MovableEnvironment,
        id: int,
        active: bool = True
    ):
        super().__init__(module_def, env, id)
        self.fuel: float = 0.0
        self.active: bool = active
        self.menv = env

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
                thrust = self.module_def.thrust
                self.env.get_net(NetworkResource.Thrust).add(self.id, thrust)
            elif phase == UpdatePhase.Execution:
                consumption = 0
                if self.menv.get_moving_state() == MovingState.Move:
                    consumption = min(dt / CYCLE_DURATION, 1.0)
                elif self.menv.get_moving_state() == MovingState.Maneuvering:
                    consumption = min(dt / CYCLE_DURATION, 1.0) * 0.5
                    
                if consumption > 0:
                    if self.fuel <= consumption:
                        if self.env.pull(FUEL_BARREL, 1):
                            self.env.push(EMPTY_BARREL, 1)
                            self.fuel += 1.0
                    self.fuel -= min(consumption, self.fuel)
                    self.env.get_net(NetworkResource.Weight).add(self.id, self.fuel * FUEL_WEIGHT)

    def onAttached(self, env: Environment):
        self.update(0.0, UpdatePhase.Anounce)