import math


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
def point_at_distance(x1: float, y1: float, x2: float, y2: float, delta: float) -> tuple[float, float]:
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    return (x1 + (dx / distance) * delta, y1 + (dy / distance) * delta)