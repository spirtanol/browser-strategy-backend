from typing import Protocol, Optional

from pydantic import BaseModel

from app.services.ship.client import ClientShipService
from app.services.platform.client import ClientPlatformService
from app.services.market import MarketService


class ResolverContext(Protocol):
    client_ship_service: ClientShipService
    client_platform_service: ClientPlatformService
    market_service: MarketService

class ResolveResult(BaseModel):
    success: bool
    message: Optional[str] = None
