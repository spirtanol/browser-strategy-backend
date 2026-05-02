from typing import Optional

from app.repositories.ship import ShipRepository, ShipEntity


class ShipService:
    def __init__(self, repository: ShipRepository):
        self.repository = repository

    async def get_all(self):
        return await self.repository.get_all()

    async def add(self, entity: ShipEntity):
        await self.repository.save([entity])

    async def save(self, entities: list[ShipEntity]):
        await self.repository.save(entities)

    async def flush(self, entities: list[ShipEntity]):
        await self.repository.flush(entities)
    
    async def is_empty(self):
        return await self.repository.is_empty()

    async def find(self, id: int) -> Optional[ShipEntity]:
        return await self.repository.find(id)