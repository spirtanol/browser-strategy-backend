from typing import Optional, Callable

from app.core.db import Redis
from app.core.exceptions import ServiceNotLoadedError
from app.repositories.platform import PlatformRepository
from app.mappers.platform import PlatformMapper
from app.entities.platform import PlatformEntity


class CorePlatformService:
    def __init__(
        self,
        platform_repo: PlatformRepository,
        platform_mapper: PlatformMapper,
        redis_factory: Callable[[], Redis]
    ):
        self.repository = platform_repo
        self._platform_mapper = platform_mapper
        self._identity_map: dict[int, PlatformEntity] = None
        self._redis_factory = redis_factory

    async def load(self):
        entities = await self.repository.get_all()
        self._identity_map = {ent.id: ent for ent in entities}

    def get_all(self) -> list[PlatformEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self.repository.save(self._identity_map.values())

    def find(self, id: int) -> Optional[PlatformEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CorePlatformService')

        return self._identity_map.get(id, None)

    def update(self, dt: float):
        pass

    async def flush(self):
        if self._identity_map is None:
            return
        return