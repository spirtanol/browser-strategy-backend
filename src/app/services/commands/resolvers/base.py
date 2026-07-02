from typing import Protocol, Optional

from pydantic import BaseModel

from app.services.ship.client import ClientShipService
from app.services.platform.client import ClientPlatformService
from app.services.market import MarketService
from app.services.site.client import ClientSiteService


class ResolverContext(Protocol):
    client_ship_service: ClientShipService
    client_platform_service: ClientPlatformService
    market_service: MarketService
    client_site_service: ClientSiteService


class ResolveResult(BaseModel):
    success: bool
    message: Optional[str] = None
