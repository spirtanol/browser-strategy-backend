from typing import Literal, Optional
from pydantic import BaseModel

from .common import EntityState
from app.entities.commands.base import BaseCommand
from app.defs.enums import ObjectType, MovingState, MarketOrderType
from app.entities.fleet import FleetEntity
from .ship import ShipShortInfoOut


class Position(BaseModel):
    x: float
    y: float

class FleetCommandOut(BaseModel):
    name: str
    state: dict[str, str | int | float | list | None | MovingState | ObjectType, dict, MarketOrderType]

    @classmethod
    def from_entity(cls, command: BaseCommand):
        return cls(
            name=command.name,
            state=command.to_dict()
        )

class FleetStateOut(EntityState):
    entity_type: Literal['fleet'] = 'fleet'

    id: int
    name: str
    position: Position
    max_speed: float
    command: Optional[FleetCommandOut] = None
    moving_state: MovingState
    attached_to_id: Optional[int]
    attached_to_type: Optional[ObjectType]
    ships: list[ShipShortInfoOut]
    owner_id: int
    removed: bool = False

    @classmethod
    def from_entity(cls, fleet: FleetEntity) -> 'FleetStateOut':
        current_command = fleet.command_queue.get_current()

        return cls(
            id=fleet.id,
            name=fleet.name,
            position=Position(x=fleet.pos.x, y=fleet.pos.y),
            max_speed=fleet.max_speed,
            command=FleetCommandOut.from_entity(current_command) if current_command else None,
            moving_state=fleet.moving_state,
            attached_to_id=fleet.attached_to_id,
            attached_to_type=fleet.attached_to_type,
            ships=[ShipShortInfoOut.from_entity(ship) for ship in fleet.ships.values()],
            owner_id=fleet.owner_id,
        )

class FleetShortInfoOut(BaseModel):
    id: int
    name: str
    position: Position
    max_speed: float
    moving_state: MovingState
    attached_to_id: Optional[int]
    attached_to_type: Optional[ObjectType]
    ships_count: int

    @classmethod
    def from_entity(cls, fleet: FleetEntity) -> 'FleetShortInfoOut':
        return cls(
            id=fleet.id,
            name=fleet.name,
            position=Position(x=fleet.pos.x, y=fleet.pos.y),
            max_speed=fleet.max_speed,
            moving_state=fleet.moving_state,
            attached_to_id=fleet.attached_to_id,
            attached_to_type=fleet.attached_to_type,
            ships_count=len(fleet.ships),
        )