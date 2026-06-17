from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, Optional
from collections.abc import Awaitable

from app.models.market_order import MarketOrder
from app.services.market import MarketService

if TYPE_CHECKING:
    from .ship import ShipEntity
    from .platform import PlatformEntity
    from .user import UserEntity

class World(Protocol):
    def find_ship(self, id: int) -> Optional[ShipEntity]: ...
    def find_platform(self, id: int) -> Optional[PlatformEntity]: ...
    def find_user(self, id: int) -> Optional[UserEntity]: ...
    def add_async_action(self, action: callable[[], Awaitable[any]]): ...
    def get_market_service(self) -> MarketService: ...