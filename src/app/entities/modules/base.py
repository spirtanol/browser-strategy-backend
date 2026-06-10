from typing import Optional, TypeVar
import enum

from app.defs.modules import ModuleDef
from app.entities.environment import Environment, NetworkResource, ResourcesPool


T = TypeVar('T', bound='BaseModule')

class UpdatePhase(enum.IntEnum):
    Anounce = 1
    Balance = 2
    Execution = 3

class BaseModule:
    def __init__(
        self, 
        module_def: ModuleDef,
        env: Environment,
        id: int,
    ):
        self.id = id
        self.module_def = module_def
        self._hp = module_def.hp
        self.env = env

    def to_dict(self) -> dict[str, any]:
        return {
            'id': self.id,
            'hp': self._hp
        }

    @classmethod
    def from_dict(cls, module_def: ModuleDef, env: Environment, data: dict) -> T:
        instance = cls(module_def, env, 0)
        instance.load_state(data)
        return instance

    def load_state(self, state: dict[str, any]):
        self.id = state.get('id', 0)
        self._hp = state.get('hp', self.module_def.hp)

    def update(self, dt: float, phase: UpdatePhase):
        pass

    def attached(self, env: Environment):
        self.env = env
        self.env.get_net(NetworkResource.Weight).add(self.id, self.module_def.weight)
        if self.module_def.floatage > 0:
            self.env.get_net(NetworkResource.Floatage).add(self.id, self.module_def.floatage)
        self.env.get_net(NetworkResource.HP).add(self.id, self.module_def.hp)
        self.onAttached(env)

    def detached(self):
        if self.env:
            self.env.get_net(NetworkResource.Weight).remove(self.id)
            self.env.get_net(NetworkResource.Floatage).remove(self.id)
            self.env.get_net(NetworkResource.HP).remove(self.id)
            self.onDetached()
            self.env = None

    def onAttached(self, env: Environment):
        pass

    def onDetached(self):
        pass