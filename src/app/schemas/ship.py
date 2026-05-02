from pydantic import BaseModel


class ShipInfoResponse(BaseModel):
    id: int
    name: str
    hunger: float
    crew: int
    storage: dict[str, int]
    weight: float
    floatage: int
    hp: int
    power: tuple[float, float]