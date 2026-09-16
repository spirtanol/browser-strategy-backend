from typing import AsyncContextManager, Optional, Callable

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.ship import ShipRepository, ShipEntity
from app.services.lifestate.registry import LifeStateRegistry
from app.schemas.ship import ShipDetailInfoOut
from app.ports.broadcast import Broadcast, ChannelMessage


class CoreShipService:
    def __init__(
        self, 
        repository: ShipRepository,
        life_state_registry: LifeStateRegistry,
        transaction: Callable[[], AsyncContextManager[None]],
        broadcast: Broadcast,
    ):
        self.repository = repository
        self._identity_map: dict[int, ShipEntity] = {}
        self._life_state_registry = life_state_registry
        self._loaded: bool = False
        self._transaction = transaction
        self._broadcast = broadcast

    async def load(self):
        async with self._transaction():
            entities = await self.repository.get_all()
            self._identity_map = {ent.id: ent for ent in entities}
            self._loaded = True

    def get_all(self) -> list[ShipEntity]:
        return list(self._identity_map.values())

    async def save(self):
        if self._identity_map:
            await self.repository.save(self.get_all())

    async def flush(self):
        if not self._loaded:
            return

        messages = []
        for entity in self.get_all():
            if self._life_state_registry.is_alive_ship(entity.id):
                dto = ShipDetailInfoOut.from_entity(entity)
                messages.append(ChannelMessage(
                    channel=f'ship:{entity.id}',
                    payload=dto.model_dump_json(),
                ))
        await self._broadcast.publish_many(messages)
    
    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[ShipEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CoreShipService')
            
        return self._identity_map.get(id, None)