from typing import Optional

from app.repositories.platform import PlatformRepository
from app.entities.platform import PlatformEntity


class PlatformService:
    def __init__(self, platform_repo: PlatformRepository):
        self._platform_repo = platform_repo

    async def find(self, id: int) -> Optional[PlatformEntity]:
        return await self._platform_repo.find(id)

    async def save(self, platform: PlatformEntity):
        await self._platform_repo.save([platform])