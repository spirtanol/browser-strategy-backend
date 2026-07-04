import asyncio
from typing import Coroutine, Any


_BACKGROUND_TASKS: set[asyncio.Task] = set()

def fire_and_forget(coro: Coroutine[Any, Any, Any], name: str | None = None) -> asyncio.Task:
    loop = asyncio.get_running_loop()
    
    task = loop.create_task(coro, name=name)
    
    _BACKGROUND_TASKS.add(task)
    
    task.add_done_callback(_BACKGROUND_TASKS.discard)
    
    return task