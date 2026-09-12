from typing import AsyncContextManager, Callable

from app.repositories.account import AccountRepository
from app.models.account import AccountModel
from app.schemas.account import CreateAccountSchema
from app.core.security import get_password_hash


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction: Callable[[], AsyncContextManager[None]],
    ):
        self._account_repo = account_repo
        self._transaction = transaction

    async def create(self, schema: CreateAccountSchema) -> AccountModel:
        async with self._transaction():
            account = AccountModel(
                email=schema.email,
                password_hash=get_password_hash(schema.password),
            )
            await self._account_repo.save(account)
            return account
