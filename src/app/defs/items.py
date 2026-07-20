from dataclasses import dataclass
import enum


@dataclass(frozen=True)
class StorageItemType:
    name: str
    weight: float # кг
    volume: float # м3


MEAL = StorageItemType(
    name='Meal', 
    weight=0.5,
    volume=0.0002
)
Fish = StorageItemType(
    name='Fish', 
    weight=5,
    volume=0.005
)
MDO = StorageItemType(
    name='MDO',
    weight=0.875,
    volume=0.0001,
)

MAP = {
    MEAL.name: MEAL,
    Fish.name: Fish,
    MDO.name: MDO
}

class NetworkResource(enum.StrEnum):
    PowerIn = 'pow_i' # Потребление
    PowerOut = 'pow_o' # Генерация
    Thrust = 'thr'
    Weight = 'wght'
    HP = 'hp'
    HarvestingFish = 'har_fish'
