from typing import AsyncContextManager, Optional, Callable

from redis.asyncio.client import Pipeline

from app.repositories.fleet import FleetRepository
from app.services.lifestate.registry import LifeStateRegistry
from app.entities.fleet import FleetEntity
from app.core.exceptions import ServiceNotLoadedError
from ..ship.core import CoreShipService
from app.core.exceptions import FleetNotFoundError
from app.schemas.fleet import FleetStateOut


class CoreFleetService:
    def __init__(
        self,
        repository: FleetRepository,
        life_state_registry: LifeStateRegistry,
        ship_service: CoreShipService,
        save_interval: int,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self.repository = repository
        self._identity_map: dict[int, FleetEntity] = {}
        self._life_state_registry = life_state_registry
        self._ship_service = ship_service
        self._save_interval = save_interval
        self._transaction = transaction
        self._loaded: bool = False
        self._pending_removed: dict[int, FleetEntity] = {}

    def _set_cache(self, pipe: Pipeline):
        for entity in self._identity_map.values():
            dto = FleetStateOut.from_entity(entity)
            pipe.set(f'c_fleet:{entity.id}', dto.model_dump_json(), ex=self._save_interval + 10)
            entity.cached = True

    async def load(self, pipe: Pipeline):
        async with self._transaction():
            await self.repository.remove_empty()
            entities = await self.repository.get_all()
            self._identity_map.clear()
            for entity in entities:
                self._identity_map[entity.id] = entity

            await self._ship_service.load()
            ships = self._ship_service.get_all()

            for ship in ships:
                fleet = self._identity_map.get(ship.fleet_id, None)
                if fleet is None:
                    raise FleetNotFoundError(ship.fleet_id)
                fleet.add_ship(ship)

            self._set_cache(pipe)
            self._loaded = True

    def get_all(self) -> list[FleetEntity]:
        return list(self._identity_map.values())

    async def save(self, pipe: Optional[Pipeline]):
        async with self._transaction():
            await self._ship_service.save()

            if self._loaded:
                await self.repository.save(self.get_all())

            if self._pending_removed:
                await self.repository.remove(list(self._pending_removed.keys()))
                self._pending_removed.clear()

            if pipe:
                self._set_cache(pipe)

    def flush(self, pipe: Pipeline):
        if not self._loaded:
            return

        for entity in self.get_all():
            if not entity.cached:
                dto = FleetStateOut.from_entity(entity)
                pipe.set(f'c_fleet:{entity.id}', dto.model_dump_json(), ex=self._save_interval + 10)
                entity.cached = True
            
            if self._life_state_registry.is_alive_fleet(entity.id):
                dto = FleetStateOut.from_entity(entity)
                pipe.publish(f'fleet:{entity.id}', dto.model_dump_json())

        for entity in self._pending_removed.values():
            pipe.delete(f'c_fleet:{entity.id}')
            if self._life_state_registry.is_alive_fleet(entity.id):
                self._life_state_registry.remove_fleet(entity.id)
                dto = FleetStateOut.from_entity(entity)
                dto.removed = True
                pipe.publish(f'fleet:{entity.id}', dto.model_dump_json())

        self._ship_service.flush(pipe)

    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[FleetEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CoreFleetService')
            
        return self._identity_map.get(id, None)
    
    async def add_fleet(self, fleet: FleetEntity):
        async with self._transaction():
            await self.repository.save([fleet])
            self._identity_map[fleet.id] = fleet
            fleet.cached = False

    def remove_fleet(self, fleet: FleetEntity):
        self._pending_removed[fleet.id] = fleet
        self._identity_map.pop(fleet.id, None)

    def get_by_owner(self, owner_id: int) -> list[FleetEntity]:
        return [fleet for fleet in self._identity_map.values() if fleet.owner_id == owner_id]

    def count_by_owner(self, owner_id: int) -> int:
        count: int = 0
        for entity in self._identity_map.values():
            if entity.owner_id == owner_id:
                count += 1
        return count