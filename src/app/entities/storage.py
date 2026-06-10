from app.defs.items import StorageItemType, MAP, NetworkResource
from .resources_pool import ResourcesPool


class Storage:
    def __init__(self):
        self._contents: dict[StorageItemType, int] = {}
        self._networks: dict[NetworkResource, ResourcesPool] = {}

    def get_total_mass(self) -> float:
        return sum(item.weight * qty for item, qty in self._contents.items())

    def push(self, item_type: StorageItemType, amount: int) -> None:
        if amount <= 0: return
        self._contents[item_type] = self._contents.get(item_type, 0) + amount

    def pull(self, item_type:StorageItemType, amount: int) -> bool:
        if amount <= 0: return

        current_amount = self._contents.get(item_type, 0)
        if current_amount >= amount:
            self._contents[item_type] -= amount
            return True
        return False

    def get_contents(self) -> dict[str, int]:
        return {item_type.name: qty for item_type, qty in self._contents.items()}

    def get_amount(self, item_type: StorageItemType) -> int:
        return self._contents.get(item_type, 0)

    def __iter__(self):
        return iter(self._contents.items())

    def from_dict(self, data: dict):
        self._contents = {}
        for type_name, qty in data.items():
            item_type = MAP.get(type_name, None)
            if item_type:
                self._contents[item_type] = qty
        
    def to_dict(self) -> dict[str, int]:
        return self.get_contents()

    def get_net(self, resource: NetworkResource) -> ResourcesPool:
        if resource not in self._networks:
            self._networks[resource] = ResourcesPool()

        return self._networks[resource]

    