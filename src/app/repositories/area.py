from typing import Callable, Optional

import sqlalchemy as sa

from app.entities.area import AreaEntity
from app.core.db import AsyncSession
from app.models.area import AreaModel
from app.mappers.area import AreaMapper


class AreaRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: AreaMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[AreaEntity]:
        session = self._session_factory()
        stmt = sa.Select(AreaModel).order_by(AreaModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[AreaEntity]:
        session = self._session_factory()
        model = await session.get(AreaModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[AreaEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = AreaModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(AreaModel), data)
            await session.flush()

    async def is_empty(self) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.Exists(AreaModel))
        return not bool(await session.scalar(q))

    async def exists(self, id: int) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.exists(AreaModel).where(AreaModel.id == id))
        return bool(await session.scalar(q))
