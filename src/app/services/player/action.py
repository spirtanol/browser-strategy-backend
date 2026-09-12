from typing import AsyncContextManager, Callable, Optional

from app.repositories.player import PlayerRepository
from app.entities.player import PlayerEntity
from app.schemas.player import CreatePlayerSchema, CreateNpcSchema


class PlayerService:
    def __init__(
        self,
        player_repo: PlayerRepository,
        transaction: Callable[[], AsyncContextManager[None]],
    ):
        self._player_repo = player_repo
        self._transaction = transaction

    async def find(self, id: int) -> Optional[PlayerEntity]:
        async with self._transaction():
            return await self._player_repo.find(id)

    async def find_by_account_id(self, account_id: int) -> Optional[PlayerEntity]:
        async with self._transaction():
            return await self._player_repo.find_by_account_id(account_id)

    async def create(self, schema: CreatePlayerSchema) -> PlayerEntity:
        async with self._transaction():
            player = PlayerEntity()
            player.name = schema.name
            player.account_id = schema.account_id
            await self._player_repo.save([player])
            return player

    async def create_npc(self, schema: CreateNpcSchema) -> PlayerEntity:
        async with self._transaction():
            player = PlayerEntity()
            player.name = schema.name
            player.is_npc = True
            await self._player_repo.save([player])
            return player

    async def save(self, player: PlayerEntity):
        async with self._transaction():
            await self._player_repo.save([player])
