from typing import Callable
from io import StringIO
from uuid import uuid4
from fastapi.responses import StreamingResponse
from fastapi import Request


async def ConvertToStreamingResponse(
    request: Request,
    call_next: Callable
):
    """
    Returns Starlette StreamingResponse if response is instance of StringIO
    https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
    """
    response = await call_next(request)
    if isinstance(response, StringIO):
        response.seek(0)

        def iterable_response(): yield from response

        stream_response = StreamingResponse(iterable_response())
        stream_response.headers['Content-Type'] = 'text/csv'
        stream_response.headers['Content-Disposition'] = f'attachment; filename={uuid4()}.csv'
        return stream_response
    return response

