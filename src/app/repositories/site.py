from typing import Callable, Optional

import sqlalchemy as sa

from app.core.db import AsyncSession
from app.mappers.site import SiteMapper
from app.models.site import SiteModel
from app.entities.site import SiteEntity
from app.schemas.player_map import MapSiteOut


class SiteRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: SiteMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_all(self) -> list[SiteEntity]:
        session = self._session_factory()
        stmt = sa.Select(SiteModel).order_by(SiteModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[SiteEntity]:
        session = self._session_factory()
        model = await session.get(SiteModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[SiteEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = SiteModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(SiteModel), data)
            await session.flush()

    async def find_known(self, ids: set[int]) -> list[MapSiteOut]:
        if not ids:
            return []
        session = self._session_factory()
        stmt = sa.select(
            SiteModel.id,
            SiteModel.x,
            SiteModel.y,
            SiteModel.site_type,
            SiteModel.site_content,
        ).where(SiteModel.id.in_(ids))
        result = await session.execute(stmt)
        return [
            MapSiteOut(
                id=row.id,
                x=row.x,
                y=row.y,
                site_type=row.site_type,
                site_content=row.site_content,
            )
            for row in result
        ]

    async def exists(self, id: int) -> bool:
        session = self._session_factory()
        q = sa.Select(sa.exists(SiteModel).where(SiteModel.id == id))
        return bool(await session.scalar(q))