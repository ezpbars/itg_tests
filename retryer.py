import asyncio
from typing import Any, Callable, Coroutine


async def retry(
    func: Callable[[], Coroutine[Any, Any, Any]], *, retries: int = 10, delay: float = 1
) -> Any:
    """If the given function raises an assertion error, retry it up to retries times.
    This prevents false failures due to syncing delays."""
    for i in range(retries):
        try:
            return await func()
        except AssertionError:
            if i == retries - 1:
                raise
            await asyncio.sleep(delay)
