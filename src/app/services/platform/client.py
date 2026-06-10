from typing import Optional

from app.entities.platform import PlatformEntity
from app.repositories.platform import PlatformRepository


class ClientPlatformService:
    def __init__(
        self, 
        platform_repository: PlatformRepository
    ):
        self._platform_repo = platform_repository

    async def find(self, id: int) -> Optional[PlatformEntity]:
        return await self._platform_repo.find(id)

    async def exists(self, id: int) -> bool:
        return await self._platform_repo.exists(id)