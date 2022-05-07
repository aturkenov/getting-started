from .base_async import BaseAsync
from .meta_service import MetaService


class BaseService(BaseAsync, metaclass=MetaService):
    """
    """


if __name__ == '__main__':
    from typing import Annotated
    import asyncio
    from .injectable import Injectable

    class A(BaseService):
        async def a(self):
            print('A', self)

    class B(BaseService):
        _s_a: Annotated[A, Injectable]
        async def b(self):
            await self._s_a.a()
            print('B', self)

    asyncio.run(B.b())

