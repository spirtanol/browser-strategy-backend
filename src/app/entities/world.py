from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .ship import ShipEntity
    from .platform import PlatformEntity

class World(Protocol):
    def find_ship(self, id: int) -> ShipEntity: ...
    def find_platform(self, id: int) -> PlatformEntity: ...
