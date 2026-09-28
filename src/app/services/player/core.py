from typing import AsyncContextManager, Optional, Callable
import json

from app.core.exceptions import ServiceNotLoadedError
from app.repositories.player import PlayerRepository
from app.repositories.player_map import PlayerMapRepository
from app.entities.player import PlayerEntity
from app.entities.player_map import PlayerMapEntity
from app.services.lifestate.registry import LifeStateRegistry
from app.schemas.player import PlayerStateOut
from src.app.services.fleet.core import CoreFleetService
from app.ports.broadcast import Broadcast, ChannelMessage
from app.ports.cache import Cache, CacheSet
from app.mappers.player_map import PlayerMapMapper


class CorePlayerService:
    def __init__(
        self,
        player_repo: PlayerRepository,
        player_map_repo: PlayerMapRepository,
        player_map_mapper: PlayerMapMapper,
        life_state_registry: LifeStateRegistry,
        transaction: Callable[[], AsyncContextManager[None]],
        fleet_service: CoreFleetService,
        broadcast: Broadcast,
        cache: Cache,
        save_interval: int,
    ):
        self._player_repo = player_repo
        self._player_map_repo = player_map_repo
        self._player_map_mapper = player_map_mapper
        self._identity_map: dict[int, PlayerEntity] = {}
        self._life_state_registry = life_state_registry
        self._transaction = transaction
        self._loaded: bool = False
        self._fleet_service = fleet_service
        self._broadcast = broadcast
        self._cache = cache
        self._save_interval = save_interval

    async def load(self):
        async with self._transaction():
            entities = await self._player_repo.get_all()
            maps = await self._player_map_repo.get_all()
            maps_by_player = {m.player_id: m for m in maps}
            for entity in entities:
                if entity.is_npc:
                    continue
                player_map = maps_by_player.get(entity.id)
                if player_map is None:
                    player_map = PlayerMapEntity()
                    player_map.player_id = entity.id
                entity.map = player_map
            self._identity_map = {ent.id: ent for ent in entities}
            self._loaded = True

    def get_all(self) -> list[PlayerEntity]:
        return list[PlayerEntity](self._identity_map.values())

    async def save(self):
        async with self._transaction():
            if self._identity_map:
                await self._player_repo.save(self.get_all())
                maps = [p.map for p in self.get_all() if p.map]
                if maps:
                    await self._player_map_repo.save(maps)

    async def flush(self):
        if not self._loaded:
            return

        messages = []
        to_set: list[CacheSet] = []
        for entity in self.get_all():
            player_map = entity.map
            if player_map is not None and not player_map.map_cached:
                to_set.append(CacheSet(
                    key=f'c_map:{entity.id}',
                    value=json.dumps(self._player_map_mapper.to_dict(player_map)),
                    ex=self._save_interval + 10,
                ))
                player_map.map_cached = True

            if self._life_state_registry.is_alive_player(entity.id):
                fleets = self._fleet_service.get_by_owner(entity.id)
                dto = PlayerStateOut.from_entity(entity, fleets)
                messages.append(ChannelMessage(
                    channel=f'player:{entity.id}',
                    payload=dto.model_dump_json(),
                ))
        await self._cache.set_many(to_set)
        await self._broadcast.publish_many(messages)

    def find(self, id: int) -> Optional[PlayerEntity]:
        if not self._loaded:
            raise ServiceNotLoadedError('CorePlayerService')
        return self._identity_map.get(id, None)
