from typing import Optional, Callable

from app.repositories.fleet import FleetRepository
from app.services.lifestate.registry import LifeStateRegistry
from app.core.db import Redis
from app.entities.fleet import FleetEntity
from app.entities.world import World
from app.core.exceptions import ServiceNotLoadedError
from ..ship.core import CoreShipService
from app.core.exceptions import FleetNotFoundError
from app.schemas.fleet import FleetStateOut


class CoreFleetService:
    def __init__(
        self,
        repository: FleetRepository,
        life_state_registry: LifeStateRegistry,
        redis_factory: Callable[[], Redis],
        ship_service: CoreShipService
    ):
        self.repository = repository
        self._identity_map: dict[int, FleetEntity] = None
        self._redis_factory = redis_factory
        self._life_state_registry = life_state_registry
        self._ship_service = ship_service

    async def load(self, world: World):
        entities = await self.repository.get_all()
        self._identity_map = {}
        for entity in entities:
            entity.bind_to_world(world)
            self._identity_map[entity.id] = entity

        await self._ship_service.load()
        ships = self._ship_service.get_all()

        for ship in ships:
            fleet = self.find(ship.fleet_id)
            if fleet is None:
                raise FleetNotFoundError(ship.fleet_id)
            fleet.add_ship(ship)

    def get_all(self) -> list[FleetEntity]:
        return self._identity_map.values()

    async def save(self):
        if self._identity_map:
            await self.repository.save(self._identity_map.values())
        await self._ship_service.save()

    async def flush(self):
        if self._identity_map is None:
            return

        redis = self._redis_factory()

        for entity in self.get_all():
            if self._life_state_registry.is_alive_fleet(entity.id):
                dto = FleetStateOut.from_entity(entity)
                await redis.publish(f'fleet:{entity.id}', dto.model_dump_json())

        await self._ship_service.flush()

    async def is_empty(self):
        return await self.repository.is_empty()

    def find(self, id: int) -> Optional[FleetEntity]:
        if self._identity_map is None:
            raise ServiceNotLoadedError('CoreFleetService')
            
        return self._identity_map.get(id, None)