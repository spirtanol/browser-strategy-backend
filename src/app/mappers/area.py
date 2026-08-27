from typing import Any

from app.entities.area import AreaEntity
from app.models.area import AreaModel


class AreaMapper:
    def _dump_state(self, entity: AreaEntity) -> dict[str, Any]:
        return {}

    def _load_state(self, entity: AreaEntity, data: dict[str, Any]):
        pass
        

    def to_dict(self, entity: AreaEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['x'] = entity.x
        data['y'] = entity.y
        data['ed'] = entity.empty_duration
        return data

    def from_dict(self, data: dict[str, Any]) -> AreaEntity:
        entity = AreaEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.x = data.get('x', 0.0)
        entity.y = data.get('y', 0.0)
        entity.empty_duration = data.get('ed', 0)
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: AreaModel) -> AreaEntity:
        entity = AreaEntity()
        entity.id = model.id
        entity.name = model.name
        entity.x = model.x
        entity.y = model.y
        entity.empty_duration = model.empty_duration
        self._load_state(entity, {})
        return entity

    def to_model_data(self, entity: AreaEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'x': entity.x,
            'y': entity.y,
            'empty_duration': entity.empty_duration
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data