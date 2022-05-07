from wampify.story import *
from .shared.base_service import BaseService as _BaseService


class BaseService(_BaseService):

    async def __ainit__(
        self
    ):
        self._story = get_current_story()

