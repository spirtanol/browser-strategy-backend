from typing import override
import math

from .storage import Storage, StorageItemType
from .environment import MovableEnvironment, ResourcesPool, NetworkResource
from app.defs.items import MEAL
from .modules.base import BaseModule, UpdatePhase
from . modules import factory as ModuleFactory
from app.utils.str_helpers import generate_random_string
from .commands.command_queue import CommandQueue
from .world import World
from app.utils import xy


HUNGER_CYCLE: float = 60 * 60 * 8
ENVIRONMENT_SPEED_FACTOR = 1.0 - 0.2

class Position:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def move_to(self, x: float, y: float, delta: float) -> bool:
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance <= delta:
            self.x = x
            self.y = y
            return True

        self.x += (dx / distance) * delta
        self.y += (dy / distance) * delta
        return False

    def distance_to(self, x: float, y: float) -> float:
        return xy.distance(self.x, self.y, x, y)

class Hull:
    def __init__(self):
        self.hp: int = 0
        self.weight: float = 0.0
        self.floatage: float = 0.0

    def to_dict(self):
        return {
            'hp': self.hp,
            'weight': self.weight,
            'floatage': self.floatage
        }

    def from_dict(self, data: dict[str, any]):
        self.hp = data.get('hp', 0)
        self.weight = data.get('weight', 0.0)
        self.floatage = data.get('floatage', 0.0)

class ShipEntity(MovableEnvironment):
    def __init__(self, id: int = 0, name: str = ''):
        self.id: int = id
        self.owner_id: int = 0
        self.counter: int = 0
        self.storage = Storage()
        self.crew: int = 0
        self.hunger: float = 0.0
        self.name: str = name
        self.modules: list[BaseModule] = []
        self.hull = Hull()
        self.pos = Position()
        self.command_queue = CommandQueue(self)
        self.onmove: bool = False

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def update(self, dt: float, world: World):
        self.onmove = False
        self.command_queue.update(dt, world)        
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
    def get_net(self, resource: NetworkResource) -> ResourcesPool:
        return self.storage.get_net(resource)

    def add_module(self, module: BaseModule):
        self.modules.append(module)
        module.attached(self)

    def remove_module(self, module: BaseModule):
        self.modules.remove(module)
        module.detached()

    @property
    def weight(self) -> float:
        weight = self.storage.get_total_mass()
        weight += self.get_net(NetworkResource.Weight).value
        return weight + self.hull.weight

    @property
    def hp(self) -> int:
        return self.get_net(NetworkResource.HP).value + self.hull.hp

    @property
    def floatage(self) -> int:
        return self.get_net(NetworkResource.Floatage).value + self.hull.floatage

    @override
    def is_moving(self) -> bool:
        return self.onmove

    @property
    def max_speed(self) -> float:
        thrust = self.get_net(NetworkResource.Thrust).value
        return thrust / self.weight * ENVIRONMENT_SPEED_FACTOR
