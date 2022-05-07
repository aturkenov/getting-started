from pydantic import BaseModel
import orjson as json


async def Jsonable(
    next,
    request
):
    """
    Converts domain model to Jsonable
    """
    output = await next(request)
    if isinstance(output, BaseModel):
        return json.loads(output.json())
    return output

