from pydantic import BaseModel


class GameCommand(BaseModel):
    entity_id: int
    action: str
    params: dict = {}

class GameCommandRequest(GameCommand):
    pass