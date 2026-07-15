from typing import override

from .storage import Storage, StorageItemType
from .resources_pool import ResourcesPool
from app.defs.items import NetworkResource
from .anchor_point import AnchorPointEntity
from app.defs.enums import ObjectType


class PlatformEntity(AnchorPointEntity):
    def __init__(self):
        super().__init__()
        self.x: float = 0.0
        self.y: float = 0.0
        self.name: str = ''
        self.owner_id: int = 0
        self.counter: int = 0
        self.storage = Storage()

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

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

    @override
    def get_type(self) -> ObjectType:
        return ObjectType.Platform