from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Literal

from app.entities.user import UserEntity
from .common import EntityState

class CreateUserSchema(BaseModel):
    name: str = Field(max_length=128)
    email: EmailStr = Field(max_length=128)
    password: str = Field(min_length=4, max_length=64)

class CreateNpcSchema(BaseModel):
    name: str = Field(max_length=128)

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

class UserStateOut(EntityState):
    entity_type: Literal['user'] = 'user'
    id: int
    name: str
    money: int

    @classmethod
    def from_entity(cls, user: UserEntity) -> 'UserStateOut':
        return cls(
            id=user.id,
            name=user.name,
            money=user.money
        )