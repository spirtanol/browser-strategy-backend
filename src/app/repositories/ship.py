from abc import ABC, abstractmethod
from typing import Optional

from app.entities.ship import ShipEntity


class ShipRepository(ABC):
    @abstractmethod
    async def find(self, id: int) -> Optional[ShipEntity]: ...

    @abstractmethod
    async def get_all(self) -> list[ShipEntity]: ...

    @abstractmethod
    async def is_empty(self) -> bool: ...

    async def flush(self, entities: list[ShipEntity]):
        pass
        
    async def save(self, entities: list[ShipEntity]):
        pass