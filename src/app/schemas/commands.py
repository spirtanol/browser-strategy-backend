import secrets

from pydantic import BaseModel, Field


def generate_6char_id() -> str:
    return secrets.token_hex(3)

class GameCommandRequest(BaseModel):
    action: str
    params: dict = Field(default_factory=dict)

class SelectShipCommand(BaseModel):
    ship_id: int

class SelectFleetCommand(BaseModel):
    fleet_id: int

class GameCommand(GameCommandRequest):
    id: str = Field(default_factory=generate_6char_id)