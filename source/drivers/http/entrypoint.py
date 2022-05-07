from typing import Callable, Any, Iterable, Mapping
from fastapi.exceptions import HTTPException
from wampify.story import *
from wampify.entrypoints import SharedEntrypoint
from wampify.signals import entrypoint_signals
from .endpoint import HTTPEndpoint


class HTTPEntrypoint(SharedEntrypoint):

    def __init__(
        self,
        procedure: Callable,
        endpoint_options: Mapping = {}
    ):
        self.endpoint = HTTPEndpoint(procedure, endpoint_options)
        self.endpoint_options = self.endpoint.options

    async def __call__(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        return await self.execute(*args, **kwargs)

    async def execute(
        self,
        args: Iterable = [],
        kwargs: Mapping = {}
    ) -> Any:
        story = create_story()
        try:
            await entrypoint_signals.fire('opened', story)
            output = await self.endpoint(args, kwargs)
            await entrypoint_signals.fire('closed', story)
        except BaseException as e:
            await entrypoint_signals.fire('raised', story, e)
            status_code = e.status_code if hasattr(e, 'status_code') else 500
            cause = e.cause if hasattr(e, 'cause') else 'Something went wrong!'
            raise HTTPException(status_code, cause)
        else:
            return output

