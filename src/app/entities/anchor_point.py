from .base import MapEntity

class AnchorPointEntity(MapEntity):
    def __init__(self):
        super().__init__()
        self.attached: set[int] = set()

    def attach(self, id: int) -> None:
        self.attached.add(id)

    def detach(self, id: int) -> None:
        self.attached.remove(id)

    def get_anchored(self) -> set[int]:
        return self.attached