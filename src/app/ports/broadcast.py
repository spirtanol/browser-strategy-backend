from dataclasses import dataclass
from typing import Protocol
from collections.abc import Sequence


@dataclass(frozen=True)
class ChannelMessage:
    channel: str
    payload: str


class Broadcast(Protocol):
    async def publish(self, channel: str, payload: str) -> None: ...
    async def publish_many(self, items: Sequence[ChannelMessage]) -> None: ...
