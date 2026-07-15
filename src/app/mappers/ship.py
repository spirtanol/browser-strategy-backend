from typing import Any

from app.entities.ship import ShipEntity, MovingState
from app.entities.ship_modules import factory as ModuleFactory
from app.models.ship import ShipModel


class ShipMapper:
    def _dump_state(self, entity: ShipEntity) -> dict[str, Any]:
        return {
            'c': entity.counter,
            'crew': entity.crew,
            'hunger': entity.hunger,
            'storage': entity.storage.to_dict(),
            'modules': [{'def': m.module_def.name, 'data': m.to_dict()} for m in entity.modules],
            'hull': entity.hull.to_dict(),
        }

    def _load_state(self, entity: ShipEntity, data: dict[str, Any]):
        entity.counter = data.get('c', 0)
        entity.crew = data.get('crew', 0)
        entity.hunger = data.get('hunger', 0.0)
        entity.storage.from_dict(data.get('storage', {}))
        entity.hull.from_dict(data.get('hull', {}))
        entity.modules = []

        # Грузим модули
        modules_data = data.get('modules', [])
        for item in modules_data:
            entity.add_module(ModuleFactory.load(item['def'], item['data']))

    def to_dict(self, entity: ShipEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['fleet_id'] = entity.fleet_id
        return data

    def from_dict(self, data: dict[str, Any]) -> ShipEntity:
        entity = ShipEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.fleet_id = data.get('fleet_id', 0)
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: ShipModel) -> ShipEntity:
        entity = ShipEntity()
        entity.id = model.id
        entity.name = model.name
        entity.fleet_id = model.fleet_id
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: ShipEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'state': self._dump_state(entity),
            'fleet_id': entity.fleet_id
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data