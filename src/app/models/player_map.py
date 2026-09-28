from typing import Any

from .base import BaseModel

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableDict


class PlayerMapModel(BaseModel):
    __tablename__ = 'player_maps'

    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete='CASCADE', onupdate='NO ACTION'),
        primary_key=True,
    )
    state: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
    )
