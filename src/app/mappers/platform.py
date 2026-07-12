from typing import Any

from .anchor_point import AnchorPointMapper
from app.entities.platform import PlatformEntity
from app.models.platform import PlatformModel


class PlatformMapper(AnchorPointMapper):
    def _dump_state(self, entity: PlatformEntity) -> dict[str, Any]:
        state_data = super()._dump_state(entity)
        state_data['c'] = entity.counter
        state_data['storage'] = entity.storage.to_dict()
        return state_data

    def _load_state(self, entity: PlatformEntity, data: dict[str, Any]):
        super()._load_state(entity, data)
        entity.counter = data.get('c', 0)
        entity.storage.from_dict(data.get('storage', {}))
        entity.modules = []

    def to_dict(self, entity: PlatformEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['owner_id'] = entity.owner_id
        data['xy'] = [entity.x, entity.y]
        return data

    def from_dict(self, data: dict[str, Any]) -> PlatformEntity:
        entity = PlatformEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.owner_id = data.get('owner_id', 0)
        entity.x, entity.y = data.get('xy', [0.0, 0.0])
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: PlatformEntity) -> PlatformEntity:
        entity = PlatformEntity()
        entity.id = model.id
        entity.name = model.name
        entity.owner_id = model.owner_id
        entity.x = model.x
        entity.y = model.y
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: PlatformEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'state': self._dump_state(entity),
            'owner_id': entity.owner_id,
            'x': entity.x,
            'y': entity.y
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data