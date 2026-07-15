from typing import Optional, Any
from app.defs.ship_hull import HullConfig, get_hull_config


class ShipHull:
    def __init__(self, size: int = 0, hull_config: Optional[HullConfig] = None):
        self.size: int = 0
        self.hull_config: Optional[HullConfig] = hull_config

    def to_dict(self):
        return {
            'conf': self.hull_config.name,
            'size': self.size,
        }

    def from_dict(self, data: dict[str, Any]):
        self.hull_config = get_hull_config(data.get('conf', 'base'))
        self.size = data.get('size', 1)

    def get_weight(self) -> int:
        return self.hull_config.weight_per_size * self.size

    def get_floatage(self) -> int:
        return self.hull_config.floatage_per_size * self.size

    def get_health(self) -> int:
        return self.hull_config.health_per_size * self.size

    def get_slots(self) -> tuple[int, int]:
        return self.size * self.hull_config.internal_slots_per_size, self.size * self.hull_config.external_slots_per_size

    def get_volume(self, locked_in_slots: int, locked_ex_slots: int) -> float:
        in_slots, ex_slots = self.get_slots()
        return ((in_slots - locked_in_slots) * self.hull_config.volume_per_internal_slot) + ((ex_slots - locked_ex_slots) * self.hull_config.volume_per_external_slot)