from __future__ import annotations
from typing import TYPE_CHECKING

from ..world import World

if TYPE_CHECKING:
    from ..ship import ShipEntity


class BaseCommand:
    def __init__(self):
        self.finished = False

    def update(self, ship: ShipEntity, dt: float, world: World):
        pass

    def to_dict(self) -> dict[str, any]:
        return {}

    def from_dict(self, data: dict[str, any]):
        pass