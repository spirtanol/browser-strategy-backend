import asyncio
import json
from typing import AsyncContextManager, AsyncGenerator, Callable, Optional
from logging import Logger

from app.repositories.player import PlayerRepository
from app.repositories.player_map import PlayerMapRepository
from app.repositories.platform import PlatformRepository
from app.repositories.site import SiteRepository
from app.repositories.area import AreaRepository
from app.entities.player import PlayerEntity
from app.entities.player_map import PlayerMapEntity
from app.mappers.player_map import PlayerMapMapper
from app.ports.cache import Cache
from app.ports.subscription import Subscription
from app.schemas.player_map import MapFleetOut, PlayerMapOut
from app.schemas.fleet import FleetPosOut
from app.services.lifestate.pusher import LifeStatePusher


_alive_players: dict[int, int] = {}

class ClientPlayerService:
    def __init__(
        self,
        player_repository: PlayerRepository,
        player_map_repository: PlayerMapRepository,
        player_map_mapper: PlayerMapMapper,
        platform_repository: PlatformRepository,
        site_repository: SiteRepository,
        area_repository: AreaRepository,
        cache: Cache,
        subscription: Subscription,
        life_state_pusher: LifeStatePusher,
        transaction: Callable[[], AsyncContextManager[None]]
    ):
        self._player_repo = player_repository
        self._player_map_repo = player_map_repository
        self._player_map_mapper = player_map_mapper
        self._platform_repo = platform_repository
        self._site_repo = site_repository
        self._area_repo = area_repository
        self._cache = cache
        self._subscription = subscription
        self._state_pusher = life_state_pusher
        self._transaction = transaction

    async def find(self, id: int) -> Optional[PlayerEntity]:
        async with self._transaction():
            return await self._player_repo.find(id)

    async def get_cached_map(self, player_id: int) -> Optional[PlayerMapEntity]:
        raw = await self._cache.get(f'c_map:{player_id}')
        if not raw:
            return None
        return self._player_map_mapper.from_dict(json.loads(raw))

    async def get_map(self, player_id: int) -> PlayerMapOut:
        player_map = await self.get_cached_map(player_id)
        async with self._transaction():
            if player_map is None:
                player_map = await self._player_map_repo.find(player_id)
                if player_map is None:
                    player_map = PlayerMapEntity()
            platforms = await self._platform_repo.find_known(player_map.platforms)
            sites = await self._site_repo.find_known(player_map.sites)
            areas = await self._area_repo.find_known(player_map.areas)
        fleets: list[MapFleetOut] = []
        for fleet_id in player_map.fleets:
            raw_pos = await self._cache.get(f'c_pos:fleet:{fleet_id}')
            if not raw_pos:
                continue
            pos = FleetPosOut.model_validate_json(raw_pos)
            fleets.append(MapFleetOut(
                id=fleet_id,
                x=pos.x,
                y=pos.y,
                owner_id=pos.owner_id,
                owner_name=pos.owner_name,
            ))
        return PlayerMapOut(platforms=platforms, sites=sites, areas=areas, fleets=fleets)

    async def subscribe_to_updates(self, id: int, logger: Logger) -> AsyncGenerator[str, None]:
        channel_name = f'player:{id}'
        if id in _alive_players:
            _alive_players[id] += 1
        else:
            _alive_players[id] = 1
        await self._state_pusher.keep_alive_player(id)
        last_keep_alive = asyncio.get_event_loop().time()

        try:
            async for msg in self._subscription.listen(channel_name):
                yield msg.payload

                now = asyncio.get_event_loop().time()
                if now - last_keep_alive > 60:
                    await self._state_pusher.keep_alive_player(id)
                    last_keep_alive = now
        except Exception as e:
            logger.exception('Ошибка при получении данных игрока из ядра')
        finally:
            _alive_players[id] -= 1
            if _alive_players[id] == 0:
                await self._state_pusher.put_player_to_sleep(id)
