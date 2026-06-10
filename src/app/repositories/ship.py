from typing import Callable, Optional

import sqlalchemy as sa

from app.entities.ship import ShipEntity
from app.core.db import AsyncSession
from app.models.ship import ShipModel
from app.mappers.ship import ShipMapper


class ShipRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: ShipMapper):
        self.session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[ShipEntity]:
        session = self.session_factory()
        stmt = sa.Select(ShipModel).order_by(ShipModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[ShipEntity]:
        session = self.session_factory()
        model = await session.get(ShipModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[ShipEntity]):
        session = self.session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = ShipModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(ShipModel), data)
            await session.flush()

    async def is_empty(self) -> bool:
        session = self.session_factory()
        q = sa.Select(sa.Exists(ShipModel))
        return not bool(await session.scalar(q))