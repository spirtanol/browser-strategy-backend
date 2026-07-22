from typing import AsyncContextManager, Callable, Optional

from app.repositories.ship import ShipRepository
from app.entities.ship import ShipEntity


class ShipService:
    def __init__(self, ship_repo: ShipRepository, transaction: Callable[[], AsyncContextManager[None]]):
        self._ship_repo = ship_repo
        self._transaction = transaction
        
    async def find(self, id: int) -> Optional[ShipEntity]:
        async with self._transaction():
            return await self._ship_repo.find(id)

    async def save(self, ship: ShipEntity):
        async with self._transaction():
            await self._ship_repo.save([ship])