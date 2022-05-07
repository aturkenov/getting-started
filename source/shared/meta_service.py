from typing import Type, List
from types import MethodType
from functools import wraps
from inspect import iscoroutinefunction as is_async
from .injectable import initialize


class MetaService(type):

    def __new__(
        klass,
        *args,
        **kwargs
    ):
        service = super().__new__(klass, *args, **kwargs)

        for method_name in service.__get_custom_methods__():
            service.__autoinitialize_classmethod__(method_name)

        return service

    def __get_custom_methods__(
        klass: Type
    ) -> List[str]:
        """
        Returns user defined class methods as list of strings
        """
        return [m for m in dir(klass) if m.startswith('_') is False and callable(getattr(klass, m))]

    def __autoinitialize_classmethod__(
        service: Type,
        method_name: str
    ) -> None:
        """
        Binds as_endpoint() to method.
        Returns class method as endpoint, i. e. creates service instance and autoinitialize injectable dependencies

        >>> import asyncio
        >>> 
        >>> class A(metaclass=MetaService):
        >>>     async def method(self, i: int):
        >>>         print('A')
        >>>
        >>> endpoint = A.method.as_endpoint()
        >>> asyncio.run(endpoint())
        """
        method = getattr(service, method_name)
        async_method = is_async(method)

        @wraps(method)
        async def on_call(
            *args,
            **kwargs
        ):
            self, *remained = args
            instance = await self.__initialize__()
            if async_method:
                return await method(instance, *remained, **kwargs)
            return method(instance, *remained, **kwargs)

        method.as_endpoint = lambda: MethodType(on_call, service)

    async def __initialize__(
        service_class: Type
    ):
        return await initialize(service_class)


if __name__ == '__main__':
    import asyncio

    class A(metaclass=MetaService):
        async def method(self, i: int): print('A')

    endpoint = A.method.as_endpoint()
    asyncio.run(endpoint())

