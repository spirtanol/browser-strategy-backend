from typing import AsyncContextManager, Callable, Optional

from app.repositories.fleet import FleetRepository
from app.entities.fleet import FleetEntity


class FleetService:
    def __init__(self, fleet_repo: FleetRepository, transaction: Callable[[], AsyncContextManager[None]]):
        self._repo = fleet_repo
        self._transaction = transaction

    async def find(self, id: int) -> Optional[FleetEntity]:
        async with self._transaction():
            return await self._repo.find(id)

    async def save(self, fleet: FleetEntity):
        async with self._transaction():
            await self._repo.save([fleet])