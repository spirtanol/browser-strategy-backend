import enum


class ObjectType(enum.IntEnum):
    Platform = 1
    Site = 2
    Fleet = 3

class MovingState(enum.IntEnum):
    Idle = 1
    Move = 2
    Docked = 3
    Maneuvering = 4
    Fishing = 5

class MarketOrderType(enum.IntEnum):
    Buy = 1
    Sell = 2

class ShipReassignOpType(enum.IntEnum):
    Attach = 1
    Detach = 2

class SiteType(enum.IntEnum):
    STABLE = 1
    TEMPORARY = 2

class SiteContent(enum.IntEnum):
    Fish = 1
    Ferrite = 2
    Pyrozine = 3