from typing import Protocol

from pydantic import BaseModel


class ShipTargeted(BaseModel):
    ship_id: int

class ShipCommand(ShipTargeted):
    clear_queue: bool = False
    on_top: bool = False