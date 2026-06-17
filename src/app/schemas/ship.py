from typing import Optional, Literal
from pydantic import BaseModel

from app.core.types import ObjectType, MovingState, MarketOrderType
from app.entities.ship import ShipEntity, NetworkResource
from app.entities.commands.base import BaseCommand
from .common import EntityState


class Position(BaseModel):
    x: float
    y: float

class ShipCommandOut(BaseModel):
    name: str
    state: dict[str, str | int | float | list | None | MovingState | ObjectType, dict, MarketOrderType]

    @classmethod
    def from_entity(cls, command: BaseCommand):
        return cls(
            name=command.name,
            state=command.to_dict()
        )

class ShipStateOut(EntityState):
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
    position: Position
    max_speed: float
    command: Optional[ShipCommandOut] = None
    state: MovingState
    attached_to_id: Optional[int]
    attached_to_type: Optional[ObjectType]

    @classmethod
    def from_entity(cls, ship: ShipEntity) -> 'ShipStateOut':
        current_command = ship.command_queue.get_current()

        return cls(
            id=ship.id,
            name=ship.name,
            crew=ship.crew,
            hunger=ship.hunger,
            storage=ship.storage.get_contents(),
            weight=ship.weight,
            floatage=ship.floatage,
            hp=ship.hp,
            power=(ship.get_net(NetworkResource.PowerIn).value, ship.get_net(NetworkResource.PowerOut).value),
            position=Position(x=ship.pos.x, y=ship.pos.y),
            max_speed=ship.max_speed,
            command=ShipCommandOut.from_entity(current_command) if current_command else None,
            state=ship.get_moving_state(),
            attached_to_id=ship.attached_to_id,
            attached_to_type=ship.attached_to_type
        )