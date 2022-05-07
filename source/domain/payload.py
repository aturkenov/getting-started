from datetime import datetime
from typing import MutableMapping
from pydantic import BaseModel, Extra, root_validator
from collections.abc import MutableMapping


class FDomain(BaseModel, MutableMapping):
    """
    """

    class Config:
        extra = Extra.allow

    def __iter__(self):
        for k, _ in BaseModel._iter(self, exclude_unset=True):
            yield k

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except:
            raise KeyError

    def __setitem__(self, key, value) -> None:
        setattr(self, key, value)

    def __delitem__(self, key) -> None:
        delattr(self, key)

    @root_validator(pre=True)
    def convert_isoformat_to_datetime(cls, values):
        for key, value in values.items():
            try:
                values[key] = datetime.fromisoformat(value)
            except:
                pass

        return values

