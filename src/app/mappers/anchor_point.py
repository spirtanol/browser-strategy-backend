from typing import Any

from app.entities.anchor_point import AnchorPointEntity


class AnchorPointMapper:
    def _dump_state(self, entity: AnchorPointEntity) -> dict[str, Any]:
        return {
            'attached': list(entity.attached)
        }

    def _load_state(self, entity: AnchorPointEntity, data: dict[str, Any]):
        entity.attached = set(data.get('attached', []))