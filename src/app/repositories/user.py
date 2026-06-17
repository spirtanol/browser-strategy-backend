from typing import Callable, Optional

import sqlalchemy as sa

from app.models.user import UserModel
from app.entities.user import UserEntity
from app.core.db import AsyncSession
from app.mappers.user import UserMapper


class UserRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession], mapper: UserMapper):
        self._session_factory = session_factory
        self._mapper = mapper

    async def find_model(self, id: int) -> Optional[UserModel]:
        session = self._session_factory()
        return await session.get(UserModel, id)

    async def find_model_by_email(self, email: str) -> Optional[UserModel]:
        session = self._session_factory()
        stmt = sa.select(UserModel).where(UserModel.email == email)
        res = await session.execute(stmt)
        return res.scalars().first()

    async def save_model(self, user: UserModel):
        session = self._session_factory()
        session.add(user)
        await session.flush()

    async def get_all(self) -> list[UserEntity]:
        session = self._session_factory()
        stmt = sa.Select(UserModel).order_by(UserModel.id)
        result = await session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.from_model(m) for m in models]

    async def find(self, id: int) -> Optional[UserEntity]:
        session = self._session_factory()
        model = await session.get(UserModel, id)
        
        if model:
            return self._mapper.from_model(model)
        return None

    async def save(self, entities: list[UserEntity]):
        session = self._session_factory()
        data = [
            self._mapper.to_model_data(entity)
            for entity in entities if entity.id != 0
        ]
        
        new_entities = [e for e in entities if e.id == 0]
        for new_e in new_entities:
            model = UserModel(
                **self._mapper.to_model_data(new_e)
            )
            session.add(model)
            await session.flush()
            new_e.id = model.id

        if data:
            await session.execute(sa.update(UserModel), data)
            await session.flush()