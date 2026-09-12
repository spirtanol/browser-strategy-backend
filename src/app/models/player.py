from typing import Any, Optional

from .base import BaseModel

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Integer, Boolean
from sqlalchemy.ext.mutable import MutableDict


class PlayerModel(BaseModel):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=False)
    state: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
    )
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    account_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)
