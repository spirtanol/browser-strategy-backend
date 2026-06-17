from typing import Callable, Optional

import sqlalchemy as sa

from app.entities.platform import PlatformEntity
from app.core.db import AsyncSession
from app.models.platform import PlatformModel
from app.mappers.platform import PlatformMapper


class PlatformRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: PlatformMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[PlatformEntity]:
        session = self._session_factory()
        stmt = sa.Select(PlatformModel).order_by(PlatformModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[PlatformEntity]:
        session = self._session_factory()
        model = await session.get(PlatformModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[PlatformEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = PlatformModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(PlatformModel), data)
            await session.flush()

    async def is_empty(self) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.Exists(PlatformModel))
        return not bool(await session.scalar(q))

    async def exists(self, id: int) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.exists(PlatformModel).where(PlatformModel.id == id))
        return bool(await session.scalar(q))