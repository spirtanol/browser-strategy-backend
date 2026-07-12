from typing import Any
from dataclasses import asdict

from .anchor_point import AnchorPointMapper
from app.entities.site import SiteEntity, SiteContent, SiteType
from app.models.site import SiteModel
from app.defs.deposites import Restriction


class SiteMapper(AnchorPointMapper):
    def _dump_state(self, entity: SiteEntity) -> dict[str, Any]:
        state_data = super()._dump_state(entity)
        state_data['restriction'] = asdict(entity.restriction)
        state_data['reserve'] = entity.reserve
        return state_data

    def _load_state(self, entity: SiteEntity, data: dict[str, Any]):
        super()._load_state(entity, data)
        entity.restriction = Restriction(**data.get('restriction', {}))
        entity.reserve = data.get('reserve', 0.0)

    def to_dict(self, entity: SiteEntity) -> dict[str, Any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['xy'] = [entity.x, entity.y]
        data['site_type'] = entity.site_type
        data['site_content'] = entity.site_content
        return data

    def from_dict(self, data: dict[str, Any]) -> SiteEntity:
        entity = SiteEntity()
        entity.id = data.get('id', 0)
        entity.x, entity.y = data.get('xy', [0.0, 0.0])
        entity.site_type = SiteType(data.get('site_type', SiteType.STABLE))
        entity.site_content = SiteContent(data.get('site_content', SiteContent.Fish))
        self._load_state(entity, data)
        return entity

    def from_model(self, model: SiteModel) -> SiteEntity:
        entity = SiteEntity()
        entity.id = model.id
        entity.x = model.x
        entity.y = model.y
        entity.site_type = model.site_type
        entity.site_content = model.site_content
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: SiteEntity) -> dict[str, Any]:
        data = {
            'x': entity.x,
            'y': entity.y,
            'site_type': entity.site_type,
            'site_content': entity.site_content,
            'state': self._dump_state(entity),
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data

    