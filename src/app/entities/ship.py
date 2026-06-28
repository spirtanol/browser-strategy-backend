from typing import Optional
import math
import enum

from .storage import Storage, StorageItemType
from .resources_pool import ResourcesPool
from app.defs.items import MEAL, NetworkResource
from .ship_modules.base import BaseShipModule, UpdatePhase
from . ship_modules import factory as ModuleFactory
from app.utils.str_helpers import generate_random_string
from .commands.command_queue import CommandQueue
from .world import World
from app.utils import xy
from app.defs.enums import MovingState, ObjectType
from .anchor_point import AnchorPoint


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

class ShipEntity:
    def __init__(self, id: int = 0, name: str = ''):
        self.id: int = id
        self.owner_id: int = 0
        self.counter: int = 0
        self.storage = Storage()
        self.crew: int = 0
        self.hunger: float = 0.0
        self.name: str = name
        self.modules: list[BaseShipModule] = []
        self.hull = Hull()
        self.pos = Position()
        self.command_queue = CommandQueue(self)
        self._state: MovingState = MovingState.Idle
        self.attached_to_id: Optional[int] = None
        self.attached_to_type: Optional[ObjectType] = None

    @property
    def moving_state(self) -> MovingState:
        return self._state

    @moving_state.setter
    def moving_state(self, new_state: MovingState) -> None:
        if new_state == self._state:
            return
        
        old_state = self._state
        self._state = new_state
        for module in self.modules:
            module.ship_moving_state_changed(old_state, new_state)

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def update(self, dt: float, world: World):
        self.command_queue.update(dt, world)        
        self._crew_update(dt)
        self._modules_update(dt, world)

    def _modules_update(self, dt: float, world: World):
        for phase in (UpdatePhase.Anounce, UpdatePhase.Balance, UpdatePhase.Execution):
            for module in self.modules:
                module.update(dt, phase, world)

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

    def push(self, item_type: StorageItemType, amount: int) -> None:
        self.storage.push(item_type, amount)

    def pull(self, item_type:StorageItemType, amount: int) -> bool:
        return self.storage.pull(item_type, amount)
        
    def get_amount(self, item_type: StorageItemType) -> int:
        return self.storage.get_amount(item_type)

    def get_net(self, resource: NetworkResource) -> ResourcesPool:
        return self.storage.get_net(resource)

    def add_module(self, module: BaseShipModule):
        self.modules.append(module)
        module.attached(self)

    def remove_module(self, module: BaseShipModule):
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

    @property
    def max_speed(self) -> float:
        thrust = self.get_net(NetworkResource.Thrust).value
        return thrust / self.weight * ENVIRONMENT_SPEED_FACTOR

    def attach_to(self, anchor_point: AnchorPoint) -> None:
        self.attached_to_id = anchor_point.get_id()
        self.attached_to_type = anchor_point.get_type()
        anchor_point.attach_ship(self.id)

    def detach(self, anchor_point: AnchorPoint) -> None:
        if self.attached_to_id is None:
            return
        
        self.attached_to_id = None
        self.attached_to_type = None
        anchor_point.detach_ship(self.id)