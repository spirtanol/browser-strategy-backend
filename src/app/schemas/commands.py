from pydantic import BaseModel


class GameCommand(BaseModel):
    action: str
    params: dict = {}

class GameCommandRequest(GameCommand):
    pass