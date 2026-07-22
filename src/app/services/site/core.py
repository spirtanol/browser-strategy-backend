from typing import AsyncContextManager, Callable, Optional

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.site import SiteRepository
from app.mappers.site import SiteMapper
from app.entities.site import SiteEntity
from app.entities.world import World


class CoreSiteService:
    def __init__(
        self,
        site_repo: SiteRepository,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self.repository = site_repo
        self._identity_map: dict[int, SiteEntity] = {}
        self._transaction = transaction
        self._loaded: bool = False
        
    async def load(self, world: World):
        async with self._transaction():
            entities = await self.repository.get_all()
            self._identity_map = {}
            for entity in entities:
                entity.bind_to_world(world)
                self._identity_map[entity.id] = entity
            self._loaded = True

    def get_all(self) -> list[SiteEntity]:
        return list(self._identity_map.values())

    async def save(self):
        if self._loaded:
            async with self._transaction():
                await self.repository.save(self.get_all())

    def find(self, id: int) -> Optional[SiteEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CoreSiteService')

        return self._identity_map.get(id, None)

    def flush(self):
        pass