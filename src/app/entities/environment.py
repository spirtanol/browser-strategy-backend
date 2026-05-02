from abc import ABC, abstractmethod

from app.defs.items import StorageItemType, NetworkResource
from .resources_pool import ResourcesPool


class Environment(ABC):
    @abstractmethod
    def push(self, item_type: StorageItemType, amount: int) -> None: ...

    @abstractmethod
    def pull(self, item_type:StorageItemType, amount: int) -> bool: ...
        
    @abstractmethod
    def get_amount(self, item_type: StorageItemType) -> int: ...

    @abstractmethod
    def get_suppliers(self, resource: NetworkResource) -> ResourcesPool: ...

    @abstractmethod
    def get_consumers(self, resource: NetworkResource) -> ResourcesPool: ...