from typing import AsyncContextManager, Optional, Callable

from app.repositories.area import AreaRepository
from app.entities.area import AreaEntity
from app.entities.world import World


class CoreAreaService:
    def __init__(
        self, 
        repository: AreaRepository, 
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self.repository = repository
        self._loaded: bool = False
        self._identity_map: dict[int, AreaEntity] = {}
        self._transaction = transaction

    async def load(self, world: World):
        async with self._transaction():
            entities = await self.repository.get_all()
            self._identity_map.clear()
            for entity in entities:
                self._identity_map[entity.id] = entity
                entity.bind_to_world(world)
            self._loaded = True

    def get_all(self) -> list[AreaEntity]:
        return list(self._identity_map.values())

    async def save(self):
        if self._loaded:
            async with self._transaction():
                await self.repository.save(self.get_all())

    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[AreaEntity]:
        return self._identity_map.get(id)
