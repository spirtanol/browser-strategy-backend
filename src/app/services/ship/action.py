from typing import Optional

from app.repositories.ship import ShipRepository
from app.entities.ship import ShipEntity


class ShipService:
    def __init__(self, ship_repo: ShipRepository):
        self._ship_repo = ship_repo

    async def find(self, id: int) -> Optional[ShipEntity]:
        return await self._ship_repo.find(id)

    async def save(self, ship: ShipEntity):
        await self._ship_repo.save([ship])