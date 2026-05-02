from typing import Optional

from .base import BaseModuleEntity
from .hull import HullModuleEntity
from .generator import GeneratorModuleEntity
import app.defs.modules as ModuleDefs


_MAP = {
    ModuleDefs.HULL.name: HullModuleEntity,
    ModuleDefs.GENERATOR.name: GeneratorModuleEntity
}

def module_factory(def_name: str) -> Optional[BaseModuleEntity]:
    module_def = ModuleDefs.MAP.get(def_name, None)
    module_class = _MAP.get(def_name, None)
    # TODO: доабавить запись в лог, если не нашли описание модуля или класс
    if module_def and module_class:
        return module_class(module_def)

    return None