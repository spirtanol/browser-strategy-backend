from typing import Callable, Optional

import sqlalchemy as sa

from app.core.db import AsyncSession
from app.models.account import AccountModel


class AccountRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def find(self, id: int) -> Optional[AccountModel]:
        session = self._session_factory()
        return await session.get(AccountModel, id)

    async def find_by_email(self, email: str) -> Optional[AccountModel]:
        session = self._session_factory()
        stmt = sa.select(AccountModel).where(AccountModel.email == email)
        res = await session.execute(stmt)
        return res.scalars().first()

    async def save(self, account: AccountModel):
        session = self._session_factory()
        session.add(account)
        await session.flush()
