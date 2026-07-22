from __future__ import annotations
from typing import TypedDict, Optional, Any

from .base import BaseCommand
from .factory import register_command
from app.defs.items import MAP as ItemMap


class TransferOperation(TypedDict):
    from_ship_id: int
    to_ship_id: int
    item_name: str
    quantity: int


@register_command()
class TransferCargoCommand(BaseCommand):
    name = 'transfer_cargo'

    def __init__(self, operations: Optional[list[TransferOperation]] = None):
        super().__init__()
        self.operations = operations if operations is not None else []
        if not self.operations:
            self.finished = True

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['operations'] = self.operations
        return data

    def from_dict(self, data: dict[str, Any]):
        super().from_dict(data)
        self.operations = data.get('operations', [])

    def update(self, dt: float):
        if self.finished:
            return

        fleet = self.fleet

        for op in self.operations:
            item_type = ItemMap.get(op['item_name'], None)
            if item_type is None:
                continue

            from_ship_id = op['from_ship_id']
            to_ship_id = op['to_ship_id']
            if from_ship_id == to_ship_id:
                continue

            from_ship = fleet.ships.get(from_ship_id, None)
            to_ship = fleet.ships.get(to_ship_id, None)
            if from_ship is None or to_ship is None:
                continue

            have = from_ship.storage.get_amount(item_type)
            left = op['quantity']
            if left == -1:
                left = have
            else:
                left = min(left, have)

            if left <= 0:
                continue

            transfer_volume = item_type.volume * left
            free_volume = to_ship.max_volume - to_ship.volume
            if free_volume < transfer_volume:
                left = int(free_volume / item_type.volume)

            transfer_weight = item_type.weight * left
            free_floatage = to_ship.floatage - to_ship.weight
            if free_floatage < transfer_weight:
                left = int(free_floatage / item_type.weight)

            if left <= 0:
                continue

            from_ship.storage.pull(item_type, left)
            to_ship.storage.push(item_type, left)

        self.finished = True
