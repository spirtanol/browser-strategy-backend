from dataclasses import dataclass
import enum


@dataclass(frozen=True)
class StorageItemType:
    name: str
    weight: float
    volume: float


MEAL = StorageItemType(
    name='Meal', 
    weight=0.5,
    volume=0.0002
)
EMPTY_BARREL = StorageItemType(
    name='EmptyBarrel', 
    weight=10,
    volume=0.2
)
FUEL_BARREL = StorageItemType(
    name='FuelBarrel', 
    weight=100 + EMPTY_BARREL.weight,
    volume=EMPTY_BARREL.volume
)
Fish = StorageItemType(
    name='Fish', 
    weight=5,
    volume=0.005
)


MAP = {
    MEAL.name: MEAL,
    EMPTY_BARREL.name: EMPTY_BARREL,
    FUEL_BARREL.name: FUEL_BARREL,
    Fish.name: Fish
}

class NetworkResource(enum.StrEnum):
    PowerIn = 'pow_i' # Потребление
    PowerOut = 'pow_o' # Генерация
    Thrust = 'thr'
    Weight = 'wght'
    HP = 'hp'
    HarvestingFish = 'har_fish'
