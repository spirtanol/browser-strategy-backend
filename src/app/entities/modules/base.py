from typing import Optional
import enum

from app.defs.modules import ModuleDef
from app.entities.environment import Environment, NetworkResource, ResourcesPool


class UpdatePhase(enum.IntEnum):
    Anounce = 1
    Balance = 2
    Execution = 3

class BaseModuleEntity:
    def __init__(self, module_def: ModuleDef):
        self.id: Optional[str] = None
        self.module_def = module_def
        self._hp = module_def.hp
        self.env: Optional[Environment] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'hp': self._hp
        }

    def from_dict(self, data: dict):
        self.id = data.get('id', None)
        self._hp = min(data.get('hp', self.module_def.hp), self.module_def.hp)

    def update(self, dt: float, phase: UpdatePhase):
        pass

    def attached(self, env: Environment):
        self.env = env
        self.env.get_suppliers(NetworkResource.Weight).add_pool(self.id, self.module_def.weight)
        if self.module_def.floatage > 0:
            self.env.get_suppliers(NetworkResource.Floatage).add_pool(self.id, self.module_def.floatage)
        self.env.get_suppliers(NetworkResource.HP).add_pool(self.id, self.module_def.hp)
        self.onAttached(env)

    def detached(self):
        if self.env:
            self.env.get_suppliers(NetworkResource.Weight).remove_pool(self.id)
            self.env.get_suppliers(NetworkResource.Floatage).remove_pool(self.id)
            self.env.get_suppliers(NetworkResource.HP).remove_pool(self.id)
            self.onDetached()
            self.env = None

    def onAttached(self, env: Environment):
        pass

    def onDetached(self):
        pass