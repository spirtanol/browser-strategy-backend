from typing import AsyncContextManager, Callable

from redis.asyncio.client import Pipeline

from app.defs.journal import JournalEvent
from app.models.journal import JournalEventModel
from app.repositories.journal import JournalRepository
from app.schemas.journal import JournalUnreadState
from app.services.lifestate.registry import LifeStateRegistry


class CoreJournalService:
    def __init__(
        self,
        repository: JournalRepository,
        transaction: Callable[[], AsyncContextManager[None]],
        life_state_registry: LifeStateRegistry,
    ):
        self.repository = repository
        self._transaction = transaction
        self._life_state_registry = life_state_registry
        self._pending_user_ids: set[int] = set()

    async def add(self, events: list[JournalEvent]) -> None:
        if not events:
            return
        models = [
            JournalEventModel(
                user_id=e.user_id,
                emitter_type=e.emitter_type,
                emitter_id=e.emitter_id,
                event_type=e.event_type,
                params=dict(e.params),
                severity=e.severity,
            )
            for e in events
        ]
        async with self._transaction():
            await self.repository.add(models)
        for event in events:
            self._pending_user_ids.add(event.user_id)

    async def flush(self, pipe: Pipeline) -> None:
        if not self._pending_user_ids:
            return

        alive_ids = [
            user_id
            for user_id in self._pending_user_ids
            if self._life_state_registry.is_alive_user(user_id)
        ]
        self._pending_user_ids.clear()

        if not alive_ids:
            return

        async with self._transaction():
            counts = await self.repository.count_unread_by_users(alive_ids)
            for user_id in alive_ids:
                count = counts.get(user_id, 0)
                if count > 0:
                    dto = JournalUnreadState(unread=count)
                    pipe.publish(f'journal:{user_id}', dto.model_dump_json())
