from typing import Literal, List, Union
from pydantic import BaseModel
from uuid import UUID
import orjson


ALL = '__all__'
TALL = Literal['__all__', '__All__', '__ALL__']
TISET = List[int]
TUSET = List[UUID]
TISET_OR_ALL = Union[TALL, TISET]
TUSET_OR_ALL = Union[TALL, TUSET]


class DomainModel(BaseModel):

    def to_jsonable(
        self,
        *args,
        **kwargs
    ) -> dict:
        """
        SQLAlchemy, json.dumps, jwt libs cannot serialize uuid.UUID objects, datetime.datetime
        and other objects, so we do it manually
        """
        return orjson.loads(
            self.json(*args, **kwargs)
        )

