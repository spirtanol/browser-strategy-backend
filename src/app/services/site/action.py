from typing import AsyncContextManager, Callable, Optional

from app.repositories.site import SiteRepository
from app.entities.site import SiteEntity


class SiteService:
    def __init__(self, site_repo: SiteRepository, transaction: Callable[[], AsyncContextManager[None]]):
        self._repo = site_repo
        self._transaction = transaction
        
    async def find(self, id: int) -> Optional[SiteEntity]:
        async with self._transaction():
            return await self._repo.find(id)

    async def save(self, site: SiteEntity):
        async with self._transaction():
            await self._repo.save([site])