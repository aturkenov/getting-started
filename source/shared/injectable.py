from typing import get_args, get_origin, Type, Mapping, Awaitable, Annotated


class Injectable: ...


async def _initializer(
    service_class: Type
):
    instance = service_class()
    if hasattr(instance, '__await__'):
        await instance
    return instance


async def initialize(
    service_class: Type,
    initializer: Awaitable = _initializer,
    _instances: Mapping[str, object] = None
):
    if _instances is None:
        _instances = {}
    
    # initializes class
    master_instance = await initializer(service_class)

    # sets default attribute __annotations__
    if not hasattr(master_instance, '__annotations__'):
        master_instance.__annotations__ = {}

    for subservice_name, v in master_instance.__annotations__.items():
        if get_origin(v) is not Annotated:
            continue

        try:
            subservice_class, injectable_annotation = get_args(v)
        except:
            continue

        if injectable_annotation is not Injectable:
            continue

        # gets already initialized instance
        subinstance = _instances.get(subservice_class, None)
        if subinstance is None:
            # otherwise initializes it recursively
            subinstance = await initialize(subservice_class, _initializer, _instances)
            _instances[subservice_class] = subinstance

        # sets subservice as attribute
        setattr(master_instance, subservice_name, subinstance)

    return master_instance


if __name__ == '__main__':
    import asyncio
    from .base_service import BaseService

    class AService(BaseService):
        ...

    class BService(BaseService):
        a: Annotated[AService, Injectable]

    class CService(BaseService):
        b: Annotated[BService, Injectable]

    class DService(BaseService):
        ...

    class EService(BaseService):
        ...

    class MasterService(BaseService):
        a: Annotated[AService, Injectable]
        b: Annotated[BService, Injectable]
        c: Annotated[CService, Injectable]
        d: Annotated[DService, Injectable]

    master_service: MasterService = asyncio.run(initialize(MasterService))
    print(master_service.a)
    print(master_service.b, master_service.b.a)
    print(master_service.c, master_service.c.b, master_service.c.b.a)
    print(master_service.d)

