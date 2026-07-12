from typing import Optional

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.site import SiteRepository
from app.mappers.site import SiteMapper
from app.entities.site import SiteEntity
from app.entities.world import World


class CoreSiteService:
    def __init__(
        self,
        site_repo: SiteRepository
    ):
        self.repository = site_repo
        self._identity_map: dict[int, SiteEntity] = None

    async def load(self, world: World):
        entities = await self.repository.get_all()
        self._identity_map = {}
        for entity in entities:
            entity.bind_to_world(world)
            self._identity_map[entity.id] = entity

    def get_all(self) -> list[SiteEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self.repository.save(self._identity_map.values())

    def find(self, id: int) -> Optional[SiteEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreSiteService')

        return self._identity_map.get(id, None)

    async def flush(self):
        pass