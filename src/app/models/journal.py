from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, ForeignKey, Integer, Boolean, DateTime, Index, func
from sqlalchemy.ext.mutable import MutableDict

from .base import BaseModel
from app.defs.enums import JournalEmitterType, JournalSeverity


class JournalEventModel(BaseModel):
    __tablename__ = 'journal_events'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete='CASCADE', onupdate='NO ACTION'),
        nullable=False,
    )
    emitter_type: Mapped[Optional[JournalEmitterType]] = mapped_column(Integer, nullable=True)
    emitter_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
    )
    severity: Mapped[JournalSeverity] = mapped_column(Integer, nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index('ix_journal_events_user_emitter', 'user_id', 'emitter_type', 'emitter_id'),
        Index('ix_journal_events_created_at', 'created_at'),
    )
