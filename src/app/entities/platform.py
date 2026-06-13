from typing import override

from .storage import Storage, StorageItemType
from .modules.base import BaseModule, UpdatePhase
from .environment import Environment, ResourcesPool, NetworkResource
from .anchor_point import AnchorPoint, ObjectType


class PlatformEntity(Environment, AnchorPoint):
    def __init__(self):
        self.id: int = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.name: str = ''
        self.owner_id: int = 0
        self.counter: int = 0
        self.storage = Storage()
        self.modules: list[BaseModule] = []
        self.attached_ships: set[int] = set()

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def update(self, dt: float):
        pass

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

    def get_type(self) -> ObjectType:
        return ObjectType.Platform

    def attach_ship(self, ship_id: int) -> None:
        self.attached_ships.add(ship_id)

    def detach_ship(self, ship_id: int) -> None:
        self.attached_ships.remove(ship_id)

    def get_id(self) -> int:
        return self.id