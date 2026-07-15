from typing import Any

from app.entities.fleet import FleetEntity, MovingState, ObjectType
from app.models.fleet import FleetModel


class FleetMapper:
    def _dump_state(self, entity: FleetEntity) -> dict[str, Any]:
        return {
            'commands': entity.command_queue.to_dict(),
            'pos': [entity.pos.x, entity.pos.y],
            'ms': entity._move_state,
            'attached_to_id': entity.attached_to_id,
            'attached_to_type': entity.attached_to_type
        }

    def _load_state(self, entity: FleetEntity, data: dict[str, Any]):
        entity.command_queue.from_dict(data.get('commands', {}))
        entity.pos.x, entity.pos.y = data.get('pos', [0.0, 0.0])
        entity._move_state = MovingState(data.get('ms', MovingState.Idle))
        entity.attached_to_id = data.get('attached_to_id', None)
        obj_type = data.get('attached_to_type', None)
        entity.attached_to_type = ObjectType(obj_type) if obj_type else None

    def to_dict(self, entity: FleetEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['owner_id'] = entity.owner_id
        return data

    def from_dict(self, data: dict[str, Any]) -> FleetEntity:
        entity = FleetEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.owner_id = data.get('owner_id', 0)
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: FleetModel) -> FleetEntity:
        entity = FleetEntity()
        entity.id = model.id
        entity.name = model.name
        entity.owner_id = model.owner_id
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: FleetEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'state': self._dump_state(entity),
            'owner_id': entity.owner_id
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data