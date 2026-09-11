from dataclasses import dataclass, field
from typing import Any, Optional

from app.defs.enums import JournalEmitterType, JournalSeverity


@dataclass
class JournalEvent:
    user_id: int
    event_type: str
    severity: JournalSeverity
    params: dict[str, Any] = field(default_factory=dict)
    emitter_type: Optional[JournalEmitterType] = None
    emitter_id: Optional[int] = None
