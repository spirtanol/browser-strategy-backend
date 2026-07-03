from typing import Optional

from app.repositories.site import SiteRepository
from app.entities.site import SiteEntity


class SiteService:
    def __init__(self, site_repo: SiteRepository):
        self._repo = site_repo

    async def find(self, id: int) -> Optional[SiteEntity]:
        return await self._repo.find(id)

    async def save(self, site: SiteEntity):
        await self._repo.save([site])