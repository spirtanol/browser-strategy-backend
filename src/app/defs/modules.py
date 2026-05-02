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

HULL = ModuleDef('hull', 500, 800, 100)
ENGINE = ModuleDef('engine', 750, 0, 100)
GENERATOR = GeneratorModuleDef('generator', 750, 0, 100, 100)

MAP = {
    HULL.name: HULL,
    ENGINE.name: ENGINE,
    GENERATOR.name: GENERATOR
}