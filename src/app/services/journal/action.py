from typing import AsyncContextManager, Callable

from app.models.journal import JournalEventModel
from app.repositories.journal import JournalRepository


class JournalService:
    def __init__(
        self,
        repository: JournalRepository,
        transaction: Callable[[], AsyncContextManager[None]],
    ):
        self._repo = repository
        self._transaction = transaction

    async def list_by_user(self, user_id: int, offset: int, limit: int) -> list[JournalEventModel]:
        async with self._transaction():
            return await self._repo.list_by_user(user_id, offset, limit)

    async def mark_readed_user_events(self, user_id: int, ids: list[int]) -> None:
        async with self._transaction():
            await self._repo.mark_read(user_id, ids)

    async def count_unread(self, user_id: int) -> int:
        async with self._transaction():
            return await self._repo.count_unread(user_id)
