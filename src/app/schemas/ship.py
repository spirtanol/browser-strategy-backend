from typing import Optional, Literal
from pydantic import BaseModel

from app.defs.enums import ObjectType, MovingState, MarketOrderType
from app.entities.ship import ShipEntity, NetworkResource
from app.entities.commands.base import BaseCommand
from .common import EntityState


class ShipShortInfoOut(BaseModel):
    id: int
    name: str
    crew: int
    max_speed: float

    @classmethod
    def from_entity(cls, ship: ShipEntity) -> "ShipShortInfo":
        return cls(
            id=ship.id,
            name=ship.name,
            crew=ship.crew,
            max_speed=ship.max_speed
        )

class ShipDetailInfoOut(EntityState):
    entity_type: Literal['ship'] = 'ship'

    id: int
    name: str
    hunger: float
    crew: int
    storage: dict[str, int]
    weight: float
    floatage: int
    hp: int
    power: tuple[float, float]
    max_speed: float
    max_volume: float
    volume: float

    @classmethod
    def from_entity(cls, ship: ShipEntity) -> 'ShipStateOut':
        return cls(
            id=ship.id,
            name=ship.name,
            crew=ship.crew,
            hunger=ship.hunger,
            storage=ship.storage.get_contents(),
            weight=ship.weight,
            floatage=ship.floatage,
            hp=ship.hp,
            power=(ship.storage.get_net(NetworkResource.PowerIn).value, ship.storage.get_net(NetworkResource.PowerOut).value),
            max_speed=ship.max_speed,
            max_volume=ship.max_volume,
            volume=ship.volume
        )