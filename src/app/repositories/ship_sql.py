from typing import Callable, override

import sqlalchemy as sa

from .ship import ShipRepository, ShipEntity, Optional
from app.core.db import AsyncSession
from app.models.ship import ShipModel


class ShipSQLRepository(ShipRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self.session_factory = session_factory

    @override
    async def get_all(self) -> list[ShipEntity]:
        session = self.session_factory()
        stmt = sa.Select(ShipModel).order_by(ShipModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @override
    async def find(self, id: int) -> Optional[ShipEntity]:
        session = self.session_factory()
        model = await session.get(ShipModel, id)
        
        if model:
            return self._to_entity(model)
        return None

    @override
    async def save(self, entities: list[ShipEntity]):
        session = self.session_factory()
        data = [
            {
                "id": entity.id,
                "name": entity.name,
                "state": entity.dump_state()
            }
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = ShipModel(
                name=new_e.name,
                state=new_e.dump_state()
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(ShipModel), data)
            await session.flush()

    def _to_entity(self, model: ShipModel) -> ShipEntity:
        entity = ShipEntity(
            id=model.id,
            name=model.name
        )
        entity.load_state(model.state)
        return entity

    @override
    async def is_empty(self) -> bool:
        session = self.session_factory()
        q = sa.Select(sa.Exists(ShipModel))
        return not bool(await session.scalar(q))