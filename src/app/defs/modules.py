from dataclasses import dataclass

from .enums import SiteContent

@dataclass
class ModuleDef:
    name: str
    weight: float
    hp: int

@dataclass
class GeneratorModuleDef(ModuleDef):
    fuel_consumption: float
    output: float

@dataclass
class EngineModuleDef(ModuleDef):
    fuel_consumption: float
    thrust: float

@dataclass
class HarvesterModuleDef(ModuleDef):
    harvest_power: float
    energy_consumption: float
    resource_type: SiteContent

BaseEngine = EngineModuleDef(
    name='engine', 
    weight=750, 
    hp=100, 
    fuel_consumption=5, 
    thrust=6000
)

BaseGenerator = GeneratorModuleDef(
    name='generator', 
    weight=750, 
    hp=100, 
    fuel_consumption=1, 
    output=100
)

FishNet = HarvesterModuleDef(
    name='fish_net', 
    weight=500.0, 
    hp=200, 
    energy_consumption=30.0,
    harvest_power=3.0,
    resource_type=SiteContent.Fish
)

MAP = {
    BaseEngine.name: BaseEngine,
    BaseGenerator.name: BaseGenerator,
    FishNet.name: FishNet
}