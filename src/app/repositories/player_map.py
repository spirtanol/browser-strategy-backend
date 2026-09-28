from typing import Callable, Optional

import sqlalchemy as sa

from app.models.player_map import PlayerMapModel
from app.entities.player_map import PlayerMapEntity
from app.core.db import AsyncSession
from app.mappers.player_map import PlayerMapMapper


class PlayerMapRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: PlayerMapMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[PlayerMapEntity]:
        session = self._session_factory()
        stmt = sa.Select(PlayerMapModel).order_by(PlayerMapModel.player_id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, player_id: int) -> Optional[PlayerMapEntity]:
        session = self._session_factory()
        model = await session.get(PlayerMapModel, player_id)

        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[PlayerMapEntity]):
        session = self._session_factory()
        entities = [e for e in entities if e.player_id]
        if not entities:
            return

        ids = [e.player_id for e in entities]
        existing = set((await session.scalars(
            sa.select(PlayerMapModel.player_id).where(PlayerMapModel.player_id.in_(ids))
        )).all())

        to_update = []
        for entity in entities:
            data = self._mapper.to_model_data(entity)
            if entity.player_id in existing:
                to_update.append(data)
            else:
                session.add(PlayerMapModel(**data))

        if to_update:
            await session.execute(sa.update(PlayerMapModel), to_update)
        await session.flush()
