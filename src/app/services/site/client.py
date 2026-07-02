from typing import Optional

from app.entities.site import SiteEntity
from app.repositories.site import SiteRepository


class ClientSiteService:
    def __init__(
        self, 
        site_repository: SiteRepository
    ):
        self._site_repo = site_repository

    async def find(self, id: int) -> Optional[SiteEntity]:
        return await self._site_repo.find(id)

    async def exists(self, id: int) -> bool:
        return await self._site_repo.exists(id)