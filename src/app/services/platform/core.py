from typing import Optional

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.platform import PlatformRepository
from app.entities.platform import PlatformEntity
from app.entities.world import World


class CorePlatformService:
    def __init__(
        self,
        platform_repo: PlatformRepository
    ):
        self.repository = platform_repo
        self._identity_map: dict[int, PlatformEntity] = None

    async def load(self, world: World):
        entities = await self.repository.get_all()
        self._identity_map = {}
        for entity in entities:
            entity.bind_to_world(world)
            self._identity_map[entity.id] = entity

    def get_all(self) -> list[PlatformEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self.repository.save(self._identity_map.values())

    def find(self, id: int) -> Optional[PlatformEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CorePlatformService')

        return self._identity_map.get(id, None)

    async def flush(self):
        pass