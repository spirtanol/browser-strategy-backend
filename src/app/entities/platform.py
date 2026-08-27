from __future__ import annotations
from typing import Optional, TYPE_CHECKING, override

from .storage import Storage, StorageItemType
from .resources_pool import ResourcesPool
from app.defs.items import NetworkResource
from .anchor_point import AnchorPointEntity
from app.defs.enums import ObjectType

if TYPE_CHECKING:
    from .area import AreaEntity
    from .world import World

class PlatformEntity(AnchorPointEntity):
    def __init__(self):
        super().__init__()
        self.x: float = 0.0
        self.y: float = 0.0
        self.name: str = ''
        self.owner_id: int = 0
        self.counter: int = 0
        self.storage = Storage()
        self.area: Optional[AreaEntity] = None

    def get_counter(self) -> int:
        self.counter += 1
        return self.counter

    def push(self, item_type: StorageItemType, amount: int) -> None:
        self.storage.push(item_type, amount)

    def pull(self, item_type:StorageItemType, amount: int) -> bool:
        return self.storage.pull(item_type, amount)
        
    def get_amount(self, item_type: StorageItemType) -> int:
        return self.storage.get_amount(item_type)

    def get_net(self, resource: NetworkResource) -> ResourcesPool:
        return self.storage.get_net(resource)

    @override
    def get_type(self) -> ObjectType:
        return ObjectType.Platform

    @override
    def bind_to_world(self, world: World):
        super().bind_to_world(world)
        area = world.get_area_at(self.x, self.y)
        if area is not None:
            area.bind_platform(self)