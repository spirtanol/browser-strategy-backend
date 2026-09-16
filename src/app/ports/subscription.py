from typing import Protocol
from collections.abc import AsyncGenerator

from app.ports.broadcast import ChannelMessage


class Subscription(Protocol):
    def listen(self, *channels: str) -> AsyncGenerator[ChannelMessage, None]: ...
