from abc import ABC, abstractmethod

from app.defs.items import StorageItemType, NetworkResource
from .resources_pool import ResourcesPool
from app.core.types import MovingState


class Environment(ABC):
    @abstractmethod
    def push(self, item_type: StorageItemType, amount: int) -> None: ...

    @abstractmethod
    def pull(self, item_type:StorageItemType, amount: int) -> bool: ...
        
    @abstractmethod
    def get_amount(self, item_type: StorageItemType) -> int: ...

    @abstractmethod
    def get_net(self, resource: NetworkResource) -> ResourcesPool: ...

class MovableEnvironment(Environment):
    @abstractmethod
    def get_moving_state(self) -> MovingState: ...