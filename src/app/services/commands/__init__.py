from typing import Protocol, Optional

from pydantic import BaseModel

from app.services.ship.client import ClientShipService


class ResolverContext(Protocol):
    client_ship_service: ClientShipService

class ResolveResult(BaseModel):
    success: bool
    message: Optional[str] = None


