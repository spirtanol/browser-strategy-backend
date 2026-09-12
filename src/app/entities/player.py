from typing import Optional


class PlayerEntity:
    def __init__(self):
        self.id: int = 0
        self.is_npc = False
        self.name = ''
        self.money: int = 0
        self.account_id: Optional[int] = None

    def update(self, dt: float):
        pass
