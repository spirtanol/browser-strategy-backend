import math


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
def point_at_distance(x1: float, y1: float, x2: float, y2: float, delta: float) -> tuple[float, float]:
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    return (x1 + (dx / distance) * delta, y1 + (dy / distance) * delta)

class Position:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def move_to(self, x: float, y: float, delta: float) -> bool:
        dx = x - self.x
        dy = y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= delta:
            self.x = x
            self.y = y
            return True

        self.x += (dx / dist) * delta
        self.y += (dy / dist) * delta
        return False

    def distance_to(self, x: float, y: float) -> float:
        return distance(self.x, self.y, x, y)

    def xy(self, x: float, y: float):
        self.x = x
        self.y = y