from typing import Callable, Optional

import sqlalchemy as sa

from app.entities.fleet import FleetEntity
from app.core.db import AsyncSession
from app.models.fleet import FleetModel
from app.mappers.fleet import FleetMapper


class FleetRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: FleetMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[FleetEntity]:
        session = self._session_factory()
        stmt = sa.Select(FleetModel).order_by(FleetModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[FleetEntity]:
        session = self._session_factory()
        model = await session.get(FleetModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[FleetEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = FleetModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(FleetModel), data)
            await session.flush()

    async def is_empty(self) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.Exists(FleetModel))
        return not bool(await session.scalar(q))