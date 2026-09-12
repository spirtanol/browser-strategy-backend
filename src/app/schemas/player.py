from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

from app.entities.player import PlayerEntity
from src.app.entities.fleet import FleetEntity
from src.app.schemas.fleet import FleetShortInfoOut
from .common import EntityState

class CreatePlayerSchema(BaseModel):
    name: str = Field(max_length=128)
    account_id: int

class CreateNpcSchema(BaseModel):
    name: str = Field(max_length=128)

class PlayerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

class PlayerStateOut(EntityState):
    entity_type: Literal['player'] = 'player'
    id: int
    name: str
    money: int
    fleets: list[FleetShortInfoOut]

    @classmethod
    def from_entity(cls, player: PlayerEntity, fleets: list[FleetEntity]) -> 'PlayerStateOut':
        return cls(
            id=player.id,
            name=player.name,
            money=player.money,
            fleets=[FleetShortInfoOut.from_entity(fleet) for fleet in fleets]
        )
