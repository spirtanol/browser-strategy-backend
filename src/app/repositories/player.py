from typing import Callable, Optional

import sqlalchemy as sa

from app.models.player import PlayerModel
from app.entities.player import PlayerEntity
from app.core.db import AsyncSession
from app.mappers.player import PlayerMapper


class PlayerRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: PlayerMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[PlayerEntity]:
        session = self._session_factory()
        stmt = sa.Select(PlayerModel).order_by(PlayerModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[PlayerEntity]:
        session = self._session_factory()
        model = await session.get(PlayerModel, id)

        if model:
            return self._mapper.from_model(model)
        return None

    async def find_by_account_id(self, account_id: int) -> Optional[PlayerEntity]:
        session = self._session_factory()
        stmt = sa.select(PlayerModel).where(PlayerModel.account_id == account_id)
        model = (await session.execute(stmt)).scalars().first()
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[PlayerEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]

        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = PlayerModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(PlayerModel), data)
            await session.flush()
