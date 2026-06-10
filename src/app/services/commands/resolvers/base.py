from typing import Protocol, Optional

from pydantic import BaseModel

from app.services.ship.client import ClientShipService
from app.services.platform.client import ClientPlatformService


class ResolverContext(Protocol):
    client_ship_service: ClientShipService
    client_platform_service: ClientPlatformService


class ResolveResult(BaseModel):
    success: bool
    message: Optional[str] = None
