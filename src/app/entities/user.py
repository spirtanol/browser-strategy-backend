class UserEntity:
    def __init__(self):
        self.id: int = 0
        self.is_npc = False
        self.name = ''
        self.money: int = 0
    
    def update(self, dt: float):
        pass
