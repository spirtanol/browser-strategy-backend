from typing import AsyncContextManager, Callable, Optional

from app.repositories.area import AreaRepository, AreaEntity


class AreaService:
    def __init__(self, repository: AreaRepository, transaction: Callable[[], AsyncContextManager[None]]):
        self._repo = repository
        self._transaction = transaction

    async def find(self, id: int) -> Optional[AreaEntity]:
        async with self._transaction():
            return await self._repo.find(id)

    async def save(self, area: AreaEntity):
        async with self._transaction():
            await self._repo.save([area])