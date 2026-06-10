import functools

from app.core.disposer import dispose


def cleanup(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        finally:
            await dispose()
    return wrapper