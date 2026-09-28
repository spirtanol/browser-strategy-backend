from typing import Any

from app.entities.player_map import PlayerMapEntity
from app.models.player_map import PlayerMapModel


class PlayerMapMapper:
    def _dump_state(self, entity: PlayerMapEntity) -> dict[str, Any]:
        return {
            'areas': list(entity.areas),
            'sites': list(entity.sites),
            'platforms': list(entity.platforms),
            'fleets': list(entity.fleets),
        }

    def _load_state(self, entity: PlayerMapEntity, data: dict[str, Any]):
        entity.areas = set(data.get('areas', []))
        entity.sites = set(data.get('sites', []))
        entity.platforms = set(data.get('platforms', []))
        entity.fleets = set(data.get('fleets', []))

    def to_dict(self, entity: PlayerMapEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['player_id'] = entity.player_id
        return data

    def from_model(self, model: PlayerMapModel) -> PlayerMapEntity:
        entity = PlayerMapEntity()
        entity.player_id = model.player_id
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: PlayerMapEntity) -> dict[str, Any]:
        return {
            'player_id': entity.player_id,
            'state': self._dump_state(entity),
        }

    def from_dict(self, data: dict[str, Any]) -> PlayerMapEntity:
        entity = PlayerMapEntity()
        entity.player_id = data.get('player_id', 0)
        self._load_state(entity, data)
        return entity
