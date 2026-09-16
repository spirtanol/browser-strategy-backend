from logging import Logger
from typing import AsyncGenerator

from app.ports.subscription import Subscription


class ClientJournalService:
    def __init__(self, subscription: Subscription):
        self._subscription = subscription

    async def subscribe_to_updates(self, user_id: int, logger: Logger) -> AsyncGenerator[str, None]:
        try:
            async for msg in self._subscription.listen(f'journal:{user_id}'):
                yield msg.payload
        except Exception:
            logger.exception('Ошибка при получении журнала из ядра')
