from typing import AsyncContextManager, Optional, Callable

from redis.asyncio.client import Pipeline

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.player import PlayerRepository
from app.entities.player import PlayerEntity
from app.services.lifestate.registry import LifeStateRegistry
from app.schemas.player import PlayerStateOut
from src.app.services.fleet.core import CoreFleetService


class CorePlayerService:
    def __init__(
        self,
        player_repo: PlayerRepository,
        life_state_registry: LifeStateRegistry,
        transaction: Callable[[], AsyncContextManager[None]],
        fleet_service: CoreFleetService,
    ):
        self._player_repo = player_repo
        self._identity_map: dict[int, PlayerEntity] = {}
        self._life_state_registry = life_state_registry
        self._transaction = transaction
        self._loaded: bool = False
        self._fleet_service = fleet_service

    async def load(self):
        async with self._transaction():
            entities = await self._player_repo.get_all()
            self._identity_map = {ent.id: ent for ent in entities}
            self._loaded = True

    def get_all(self) -> list[PlayerEntity]:
        return list[PlayerEntity](self._identity_map.values())

    async def save(self):
        async with self._transaction():
            if self._identity_map:
                await self._player_repo.save(self.get_all())

    def flush(self, pipe: Pipeline):
        if not self._loaded:
            return

        for entity in self.get_all():
            if self._life_state_registry.is_alive_player(entity.id):
                fleets = self._fleet_service.get_by_owner(entity.id)
                dto = PlayerStateOut.from_entity(entity, fleets)
                pipe.publish(f'player:{entity.id}', dto.model_dump_json())

    def find(self, id: int) -> Optional[PlayerEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CorePlayerService')
        return self._identity_map.get(id, None)
