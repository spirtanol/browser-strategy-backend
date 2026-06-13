from dataclasses import dataclass


@dataclass
class ModuleDef:
    name: str
    weight: float
    floatage: float
    hp: int

@dataclass
class GeneratorModuleDef(ModuleDef):
    output: float

@dataclass
class EngineModuleDef(ModuleDef):
    thrust: float

ENGINE = EngineModuleDef('engine', 750, 0, 100, 6000)
GENERATOR = GeneratorModuleDef('generator', 750, 0, 100, 100)

MAP = {
    ENGINE.name: ENGINE,
    GENERATOR.name: GENERATOR
}