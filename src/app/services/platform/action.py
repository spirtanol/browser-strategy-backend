from typing import AsyncContextManager, Callable, Optional

from app.repositories.platform import PlatformRepository
from app.entities.platform import PlatformEntity


class PlatformService:
    def __init__(self, platform_repo: PlatformRepository, transaction: Callable[[], AsyncContextManager[None]]):
        self._platform_repo = platform_repo
        self._transaction = transaction
        
    async def find(self, id: int) -> Optional[PlatformEntity]:
        async with self._transaction():
            return await self._platform_repo.find(id)

    async def save(self, platform: PlatformEntity):
        async with self._transaction():
            await self._platform_repo.save([platform])