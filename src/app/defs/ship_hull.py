from dataclasses import dataclass


@dataclass(frozen=True)
class HullConfig:
    name: str

    internal_slots_per_size: int
    external_slots_per_size: int

    volume_per_internal_slot: float
    volume_per_external_slot: float

    floatage_per_size: float
    weight_per_size: float
    health_per_size: int


BASE_HULL = HullConfig(
    name='base',
    internal_slots_per_size=4,
    external_slots_per_size=4,
    volume_per_internal_slot=5.0,
    volume_per_external_slot=3.0,
    floatage_per_size=30000.0,
    weight_per_size=10000.0,
    health_per_size=100
)

def get_hull_config(name: str) -> HullConfig:
    match (name):
        case _:
            return BASE_HULL