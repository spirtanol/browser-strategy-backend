from dataclasses import dataclass

from .enums import SiteContent

@dataclass
class ModuleDef:
    name: str
    weight: float
    hp: int
    in_slots: int
    ex_slots: int
    work_consumption: float

@dataclass
class GeneratorModuleDef(ModuleDef):
    fuel_consumption: float
    output: float

@dataclass
class EngineModuleDef(ModuleDef):
    fuel_consumption: float
    thrust: float
    wear_per_hour: float

@dataclass
class HarvesterModuleDef(ModuleDef):
    harvest_power: float
    energy_consumption: float
    resource_type: SiteContent
    wear_per_cycle: float

BaseEngine = EngineModuleDef(
    name='engine', 
    weight=1500, 
    hp=100, 
    fuel_consumption=36, 
    thrust=400,
    in_slots=1,
    ex_slots=0,
    work_consumption=3,
    wear_per_hour=0.01,
)

BaseGenerator = GeneratorModuleDef(
    name='generator', 
    weight=500, 
    hp=100, 
    fuel_consumption=7, 
    output=100,
    in_slots=1,
    ex_slots=0,
    work_consumption=1,
)

FishNet = HarvesterModuleDef(
    name='fish_net', 
    weight=500.0, 
    hp=200, 
    energy_consumption=30.0,
    harvest_power=3000.0,
    resource_type=SiteContent.Fish,
    in_slots=0,
    ex_slots=2,
    work_consumption=3,
    wear_per_cycle=0.02,
)

MAP = {
    BaseEngine.name: BaseEngine,
    BaseGenerator.name: BaseGenerator,
    FishNet.name: FishNet
}