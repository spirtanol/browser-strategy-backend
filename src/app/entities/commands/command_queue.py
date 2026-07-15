from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
from collections import deque

from .base import BaseCommand
from .factory import load as load_command
from app.defs.enums import MovingState

if TYPE_CHECKING:
    from ..fleet import FleetEntity


class CommandQueue:
    def __init__(self, fleet: FleetEntity):
        self.fleet = fleet
        self.queue: deque[BaseCommand] = deque()

    def add(self, command: BaseCommand, on_top: bool = False):
        command.queue = self
        if on_top:
            self.cancel_depends()
            self.queue.appendleft(command)
        else:
            self.queue.append(command)

    def update(self, dt: float):
        if len(self.queue) > 0:
            self.queue[0].update(dt)
            if self.queue[0].finished:
                self.queue.popleft()
                if len(self.queue) == 0:
                    if self.fleet.moving_state in (MovingState.Move, MovingState.Maneuvering):
                        self.fleet.moving_state = MovingState.Idle
            
    def to_dict(self) -> list[dict[str, Any]]:
        return [{'name': com.name, 'data': com.to_dict()} for com in self.queue]

    def from_dict(self, data: list[dict[str, Any]]):
        self.queue.clear()
        for com_item in data:
            com = load_command(com_item['name'], com_item['data'])
            com.queue = self
            self.queue.append(com)

    def get_current(self) -> Optional[BaseCommand]:
        return self.queue[0] if len(self.queue) > 0 else None

    def pop_current(self):
        if len(self.queue) > 0:
            self.queue[0].cancel()
            self.queue.popleft()
    
    def pop_last(self):
        self.queue.pop()

    def cancel_depends(self):
        if len(self.queue) > 0:
            if self.queue[0].is_dependent:
                self.queue[0].cancel()
                while self.queue[0].is_dependent:
                    self.queue.popleft()

    def cancel_all(self):
        if len(self.queue) > 0:
            self.queue[0].cancel()
            self.queue.clear()