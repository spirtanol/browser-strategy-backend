from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from collections import deque

from .base import BaseCommand
from .factory import load as load_command
from ..world import World
from app.defs.enums import MovingState

if TYPE_CHECKING:
    from ..ship import ShipEntity


class CommandQueue:
    def __init__(self, ship: ShipEntity):
        self.ship = ship
        self.queue: deque[BaseCommand] = deque()

    def add(self, command: BaseCommand, on_top: bool = False):
        if on_top:
            self.queue.appendleft(command)
        else:
            self.queue.append(command)

    def update(self, dt: float, world: World):
        if len(self.queue) > 0:
            self.queue[0].update(self.ship, dt, world)
            if self.queue[0].finished:
                self.queue.popleft()
                if len(self.queue) == 0:
                    if self.ship.state in (MovingState.Move, MovingState.Maneuvering):
                        self.ship.state = MovingState.Idle
            
    def clear(self):
        self.queue.clear()

    def to_dict(self) -> list[dict[str, any]]:
        return [{'name': com.name, 'data': com.to_dict()} for com in self.queue]

    def from_dict(self, data: list[dict[str, any]]):
        self.queue.clear()
        for com_item in data:
            com = load_command(com_item['name'], com_item['data'])
            self.queue.append(com)

    def get_current(self) -> Optional[BaseCommand]:
        return self.queue[0] if len(self.queue) > 0 else None

    def pop_current(self):
        self.queue.popleft()
    
    def pop_last(self):
        self.queue.pop()