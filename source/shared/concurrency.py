import asyncio
from typing import Coroutine, Tuple


async def run_concurrently(*aws: Coroutine) -> Tuple:
    result = await asyncio.gather(*aws, return_exceptions=True)

    for item in result:
        if isinstance(item, BaseException):
            raise item

    return result
