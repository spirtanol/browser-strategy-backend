from typing import override

from .storage import Storage, StorageItemType
from .environment import Environment, ResourcesPool, NetworkResource
from app.defs.items import MEAL
from .modules.base import BaseModuleEntity, UpdatePhase
from .modules.factory import module_factory
from app.utils.str_helpers import generate_random_string


HUNGER_CYCLE: float = 60 * 60 * 8

class ShipEntity(Environment):
    def __init__(self, id: int = 0, name: str = ''):
        self.storage = Storage()
        self.crew: int = 0
        self.hunger: float = 0.0
        self.id: int = id
        self.name: str = name
        self.modules = []

    def update(self, dt: float):
        self._crew_update(dt)
        self._modules_update(dt)

    def _modules_update(self, dt: float):
        for phase in (UpdatePhase.Anounce, UpdatePhase.Balance, UpdatePhase.Execution):
            for module in self.modules:
                module.update(dt, phase)

    def _crew_update(self, dt: float):
        if self.crew <= 0:
            return

        self.hunger += (dt / HUNGER_CYCLE)

        if self.hunger >= 1.0:
            meals_on_storage = self.storage.get_amount(MEAL)
            if meals_on_storage > 0:
                meal_consume = min(self.crew, meals_on_storage)
                self.storage.pull(MEAL, meal_consume)
                self.hunger -= meal_consume / self.crew

    def load_state(self, state: dict):
        self.crew = state.get('crew', 0)
        self.hunger = state.get('hunger', 0)
        storage_data = state.get('storage', None)
        if storage_data:
            self.storage.from_dict(storage_data)
        
        # Грузим модули
        modules_data = state.get('modules', [])
        for item in modules_data:
            module = module_factory(item['def'])
            module.from_dict(item['state'])
            self.add_module(module)

        # Встряхиваем их после загрузки
        for phase in (UpdatePhase.Anounce, UpdatePhase.Balance):
            for module in self.modules:
                module.update(0.0, phase)

    def dump_state(self) -> dict[str, any]:
        return {
            'crew': self.crew,
            'hunger': self.hunger,
            'storage': self.storage.to_dict(),
            'modules': [{'def': m.module_def.name, 'state': m.to_dict()} for m in self.modules]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShipEntity":
        obj = cls(
            id=data.get('id', 0),
            name=data.get('name', '')
        )
        obj.load_state(data.get('state', {}))

        return obj

    def to_dict(self) -> dict[str, any]:
        return {
            'id': self.id,
            'name': self.name,
            'state': self.dump_state()
        }

    @override
    def push(self, item_type: StorageItemType, amount: int) -> None:
        self.storage.push(item_type, amount)

    @override
    def pull(self, item_type:StorageItemType, amount: int) -> bool:
        return self.storage.pull(item_type, amount)
        
    @override
    def get_amount(self, item_type: StorageItemType) -> int:
        return self.storage.get_amount(item_type)

    @override
    def get_suppliers(self, resource: NetworkResource) -> ResourcesPool:
        return self.storage.get_suppliers(resource)

    @override
    def get_consumers(self, resource: NetworkResource) -> ResourcesPool:
        return self.storage.get_consumers(resource)

    def add_module(self, module: BaseModuleEntity):
        while module.id is None or module.id in (m.id for m in self.modules):
            module.id = generate_random_string(4)

        self.modules.append(module)
        module.attached(self)

    def remove_module(self, module: BaseModuleEntity):
        self.modules.remove(module)
        module.detached()

    @property
    def weight(self) -> float:
        weight = self.storage.get_total_mass()
        weight += self.get_suppliers(NetworkResource.Weight).value
        return weight

    @property
    def hp(self) -> int:
        return self.get_suppliers(NetworkResource.HP).value

    @property
    def floatage(self) -> int:
        return self.get_suppliers(NetworkResource.Floatage).value