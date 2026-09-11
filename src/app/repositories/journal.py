from typing import Callable

import sqlalchemy as sa

from app.core.db import AsyncSession
from app.models.journal import JournalEventModel


class JournalRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def add(self, models: list[JournalEventModel]) -> None:
        if not models:
            return
        session = self._session_factory()
        session.add_all(models)
        await session.flush()

    async def list_by_user(self, user_id: int, offset: int, limit: int) -> list[JournalEventModel]:
        session = self._session_factory()
        stmt = (
            sa.Select(JournalEventModel)
            .where(JournalEventModel.user_id == user_id)
            .order_by(JournalEventModel.created_at.desc(), JournalEventModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list((await session.scalars(stmt)).all())

    async def mark_read(self, user_id: int, ids: list[int]) -> None:
        if not ids:
            return
        session = self._session_factory()
        await session.execute(
            sa.update(JournalEventModel)
            .where(
                JournalEventModel.user_id == user_id,
                JournalEventModel.id.in_(ids),
            )
            .values(is_read=True)
        )
        await session.flush()

    async def count_unread(self, user_id: int) -> int:
        session = self._session_factory()
        stmt = (
            sa.select(sa.func.count())
            .select_from(JournalEventModel)
            .where(
                JournalEventModel.user_id == user_id,
                JournalEventModel.is_read == False,
            )
        )
        return int(await session.scalar(stmt) or 0)

    async def count_unread_by_users(self, user_ids: list[int]) -> dict[int, int]:
        if not user_ids:
            return {}
        session = self._session_factory()
        stmt = (
            sa.select(JournalEventModel.user_id, sa.func.count())
            .where(
                JournalEventModel.user_id.in_(user_ids),
                JournalEventModel.is_read == False,
            )
            .group_by(JournalEventModel.user_id)
        )
        rows = (await session.execute(stmt)).all()
        return {user_id: int(n) for user_id, n in rows}
