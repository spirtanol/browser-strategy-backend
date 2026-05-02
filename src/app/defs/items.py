from dataclasses import dataclass
import enum


@dataclass(frozen=True)
class StorageItemType:
    name: str
    weight: float


MEAL = StorageItemType('Meal', 0.5)
EMPTY_BARREL = StorageItemType('EmptyBarrel', 10)
FUEL_BARREL = StorageItemType('FuelBarrel', 100 + EMPTY_BARREL.weight)


MAP = {
    MEAL.name: MEAL,
    EMPTY_BARREL.name: EMPTY_BARREL,
    FUEL_BARREL.name: FUEL_BARREL
}

class NetworkResource(enum.StrEnum):
    Power = 'pow'
    Thrust = 'thr'
    Weight = 'wght'
    HP = 'hp'
    Floatage = 'float'