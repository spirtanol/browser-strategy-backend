from .base import BaseModel

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Integer, Boolean
from sqlalchemy.ext.mutable import MutableDict


class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=False)
    state: Mapped[dict[str, any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict, 
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)