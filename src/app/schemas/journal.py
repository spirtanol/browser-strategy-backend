from datetime import datetime
from typing import Any, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.defs.enums import JournalEmitterType, JournalSeverity
from .common import BaseOut


class JournalEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    emitter_type: Optional[JournalEmitterType]
    emitter_id: Optional[int]
    event_type: str
    params: dict[str, Any]
    severity: JournalSeverity
    is_read: bool
    created_at: datetime


class MarkJournalReadRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=100)


class JournalUnreadOut(BaseModel):
    unread: int


class JournalUnreadState(BaseOut):
    out_type: Literal['journal'] = 'journal'
    unread: int
