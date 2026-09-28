from typing import AsyncContextManager, Optional, Callable

from app.repositories.fleet import FleetRepository
from app.services.lifestate.registry import LifeStateRegistry
from app.entities.fleet import FleetEntity
from app.core.exceptions import ServiceNotLoadedError
from ..ship.core import CoreShipService
from app.core.exceptions import FleetNotFoundError
from app.schemas.fleet import FleetStateOut, FleetPosOut
from app.entities.world import World
from app.ports.cache import Cache, CacheSet
from app.ports.broadcast import Broadcast, ChannelMessage


class CoreFleetService:
    def __init__(
        self,
        repository: FleetRepository,
        life_state_registry: LifeStateRegistry,
        ship_service: CoreShipService,
        save_interval: int,
        transaction: Callable[[], AsyncContextManager[None]],
        cache: Cache,
        broadcast: Broadcast,
    ):
        self.repository = repository
        self._identity_map: dict[int, FleetEntity] = {}
        self._life_state_registry = life_state_registry
        self._ship_service = ship_service
        self._save_interval = save_interval
        self._transaction = transaction
        self._cache = cache
        self._broadcast = broadcast
        self._loaded: bool = False
        self._pending_removed: dict[int, FleetEntity] = {}

    def _pos_cache_item(self, fleet: FleetEntity) -> CacheSet:
        dto = FleetPosOut.from_entity(fleet)
        return CacheSet(
            key=f'c_pos:fleet:{fleet.id}',
            value=dto.model_dump_json(),
            ex=self._save_interval + 10,
        )

    async def _set_cache(self):
        items = []
        for entity in self._identity_map.values():
            dto = FleetStateOut.from_entity(entity)
            items.append(CacheSet(
                key=f'c_fleet:{entity.id}',
                value=dto.model_dump_json(),
                ex=self._save_interval + 10,
            ))
            items.append(self._pos_cache_item(entity))
            entity.cached = True
            entity.pos_cached = True
        await self._cache.set_many(items)

    async def load(self, world: World):
        async with self._transaction():
            await self.repository.remove_empty()
            entities = await self.repository.get_all()
            self._identity_map.clear()
            for entity in entities:
                self._identity_map[entity.id] = entity
                entity.bind_to_world(world)

            await self._ship_service.load()
            ships = self._ship_service.get_all()

            for ship in ships:
                fleet = self._identity_map.get(ship.fleet_id, None)
                if fleet is None:
                    raise FleetNotFoundError(ship.fleet_id)
                fleet.add_ship(ship)

            await self._set_cache()
            self._loaded = True

    def get_all(self) -> list[FleetEntity]:
        return list(self._identity_map.values())

    async def save(self):
        if not self._loaded:
            return

        async with self._transaction():
            await self._ship_service.save()

            await self.repository.save(self.get_all())

            if self._pending_removed:
                await self.repository.remove(list(self._pending_removed.keys()))
                self._pending_removed.clear()

            await self._set_cache()

    async def flush(self):
        if not self._loaded:
            return

        to_set: list[CacheSet] = []
        to_delete: list[str] = []
        messages: list[ChannelMessage] = []

        for entity in self.get_all():
            if not entity.cached:
                dto = FleetStateOut.from_entity(entity)
                to_set.append(CacheSet(
                    key=f'c_fleet:{entity.id}',
                    value=dto.model_dump_json(),
                    ex=self._save_interval + 10,
                ))
                entity.cached = True

            if not entity.pos_cached:
                to_set.append(self._pos_cache_item(entity))
                entity.pos_cached = True
            
            if self._life_state_registry.is_alive_fleet(entity.id):
                dto = FleetStateOut.from_entity(entity)
                messages.append(ChannelMessage(
                    channel=f'fleet:{entity.id}',
                    payload=dto.model_dump_json(),
                ))

        for entity in self._pending_removed.values():
            to_delete.append(f'c_fleet:{entity.id}')
            to_delete.append(f'c_pos:fleet:{entity.id}')
            if self._life_state_registry.is_alive_fleet(entity.id):
                self._life_state_registry.remove_fleet(entity.id)
                dto = FleetStateOut.from_entity(entity)
                dto.removed = True
                messages.append(ChannelMessage(
                    channel=f'fleet:{entity.id}',
                    payload=dto.model_dump_json(),
                ))

        await self._cache.set_many(to_set)
        await self._cache.delete_many(to_delete)
        await self._broadcast.publish_many(messages)
        await self._ship_service.flush()

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
            fleet.pos_cached = False

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
