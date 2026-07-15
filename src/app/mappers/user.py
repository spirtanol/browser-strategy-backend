from typing import Any

from app.entities.user import UserEntity
from app.models.user import UserModel


class UserMapper:
    def _dump_state(self, entity: UserEntity) -> dict[str, Any]:
        return {
            'money': entity.money
        }

    def _load_state(self, entity: UserEntity, data: dict[str, Any]):
        entity.money = data.get('money', 0)

    def to_dict(self, entity: UserEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['is_npc'] = entity.is_npc
        return data

    def from_model(self, model: UserModel) -> UserEntity:
        entity = UserEntity()
        entity.id = model.id
        entity.name = model.name
        entity.is_npc = model.is_npc
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: UserEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'is_npc': entity.is_npc,
            'state': self._dump_state(entity),
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data

    def from_dict(self, data: dict[str, Any]) -> UserEntity:
        entity = UserEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.is_npc = data.get('is_npc', False)
        self._load_state(entity, data)
        return entity