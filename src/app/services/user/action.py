from typing import AsyncContextManager, Callable, Optional

from app.repositories.user import UserRepository
from app.entities.user import UserEntity
from app.schemas.user import CreateUserSchema, CreateNpcSchema
from app.core.security import get_password_hash
from app.mappers.user import UserMapper
from app.models.user import UserModel


class UserService:
    def __init__(self, user_repo: UserRepository, user_mapper: UserMapper, transaction: Callable[[], AsyncContextManager[None]]):
        self._user_repo = user_repo
        self._user_mapper = user_mapper
        self._transaction = transaction
        
    async def find(self, id: int) -> Optional[UserEntity]:
        async with self._transaction():
            return await self._user_repo.find(id)

    async def create(self, schema: CreateUserSchema) -> UserEntity:
        async with self._transaction():
            user = UserModel(
                name=schema.name,
                email=schema.email,
                password_hash=get_password_hash(schema.password)
            )

            await self._user_repo.save_model(user)

            return self._user_mapper.from_model(user)

    async def create_npc(self, schema: CreateNpcSchema) -> UserEntity:
        async with self._transaction():
            user = UserModel(
                name=schema.name,
                email='npc@nomail.npc',
                is_npc=True
            )

            await self._user_repo.save_model(user)

            return self._user_mapper.from_model(user)

    async def save(self, user: UserEntity):
        async with self._transaction():
            await self._user_repo.save([user])