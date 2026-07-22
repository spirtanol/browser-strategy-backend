from typing import AsyncContextManager, Callable, Optional

from app.entities.site import SiteEntity
from app.repositories.site import SiteRepository


class ClientSiteService:
    def __init__(
        self, 
        site_repository: SiteRepository,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self._site_repo = site_repository
        self._transaction = transaction

    async def find(self, id: int) -> Optional[SiteEntity]:
        async with self._transaction():
            return await self._site_repo.find(id)

    async def exists(self, id: int) -> bool:
        async with self._transaction():
            return await self._site_repo.exists(id)