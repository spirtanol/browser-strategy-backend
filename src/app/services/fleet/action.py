from typing import Optional

from app.repositories.fleet import FleetRepository
from app.entities.fleet import FleetEntity


class FleetService:
    def __init__(self, fleet_repo: FleetRepository):
        self._repo = fleet_repo

    async def find(self, id: int) -> Optional[FleetEntity]:
        return await self._repo.find(id)

    async def save(self, fleet: FleetEntity):
        await self._repo.save([fleet])