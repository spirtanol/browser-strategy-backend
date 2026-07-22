from typing import AsyncContextManager, Callable, Optional

from app.entities.platform import PlatformEntity
from app.repositories.platform import PlatformRepository


class ClientPlatformService:
    def __init__(
        self, 
        platform_repository: PlatformRepository,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self._platform_repo = platform_repository
        self._transaction = transaction
        
    async def find(self, id: int) -> Optional[PlatformEntity]:
        async with self._transaction():
            return await self._platform_repo.find(id)

    async def exists(self, id: int) -> bool:
        async with self._transaction():
            return await self._platform_repo.exists(id)