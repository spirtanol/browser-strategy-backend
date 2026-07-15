import enum
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, ForeignKey, Float, String
from sqlalchemy.ext.mutable import MutableDict

from .base import BaseModel


class PlatformModel(BaseModel):
    __tablename__ = 'platforms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict, 
        nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='RESTRICT', onupdate='NO ACTION'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=False)