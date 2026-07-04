from typing import Protocol

from pydantic import BaseModel


class UserCommand(BaseModel):
    id: str

class ShipTargeted(UserCommand):
    ship_id: int

class ShipCommand(ShipTargeted):
    clear_queue: bool = False
    on_top: bool = False