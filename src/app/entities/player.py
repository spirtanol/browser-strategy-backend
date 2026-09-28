from typing import Optional

from src.app.entities.player_map import PlayerMapEntity


class PlayerEntity:
    def __init__(self):
        self.id: int = 0
        self.is_npc = False
        self.name = ''
        self.money: int = 0
        self.account_id: Optional[int] = None
        self.map: Optional[PlayerMapEntity] = None

    def update(self, dt: float):
        pass
