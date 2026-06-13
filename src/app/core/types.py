import enum


class ObjectType(enum.IntEnum):
    Platform = 1
    Site = 2

class MovingState(enum.IntEnum):
    Idle = 1
    Move = 2
    Docked = 3
    Maneuvering = 4