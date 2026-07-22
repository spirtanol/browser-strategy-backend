from typing import AsyncContextManager, Callable, Optional

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.platform import PlatformRepository
from app.entities.platform import PlatformEntity
from app.entities.world import World


class CorePlatformService:
    def __init__(
        self,
        platform_repo: PlatformRepository,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self.repository = platform_repo
        self._identity_map: dict[int, PlatformEntity] = {}
        self._transaction = transaction
        self._loaded: bool = False

    async def load(self, world: World):
        async with self._transaction():
            entities = await self.repository.get_all()
            self._identity_map.clear()
            for entity in entities:
                entity.bind_to_world(world)
                self._identity_map[entity.id] = entity
            self._loaded = True

    def get_all(self) -> list[PlatformEntity]:
        return list(self._identity_map.values())

    async def save(self):
        async with self._transaction():
            if self._identity_map:
                await self.repository.save(self.get_all())

    def find(self, id: int) -> Optional[PlatformEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CorePlatformService')

        return self._identity_map.get(id, None)

    def flush(self):
        pass