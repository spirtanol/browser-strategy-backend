from typing import Any

from app.entities.player import PlayerEntity
from app.models.player import PlayerModel


class PlayerMapper:
    def _dump_state(self, entity: PlayerEntity) -> dict[str, Any]:
        return {
            'money': entity.money
        }

    def _load_state(self, entity: PlayerEntity, data: dict[str, Any]):
        entity.money = data.get('money', 0)

    def to_dict(self, entity: PlayerEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['is_npc'] = entity.is_npc
        data['account_id'] = entity.account_id
        return data

    def from_model(self, model: PlayerModel) -> PlayerEntity:
        entity = PlayerEntity()
        entity.id = model.id
        entity.name = model.name
        entity.is_npc = model.is_npc
        entity.account_id = model.account_id
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: PlayerEntity) -> dict[str, Any]:
        data = {
            'name': entity.name,
            'is_npc': entity.is_npc,
            'account_id': entity.account_id,
            'state': self._dump_state(entity),
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data

    def from_dict(self, data: dict[str, Any]) -> PlayerEntity:
        entity = PlayerEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.is_npc = data.get('is_npc', False)
        entity.account_id = data.get('account_id')
        self._load_state(entity, data)
        return entity
