from pydantic import Field
from pydantic.typing import Annotated, get_origin
from typing import Callable, Any
import inspect


def make_ellipsis_default(
    procedure: Callable
):
    """
    By default Pydantic cant put ... (ellipsis) as default value for callables. So this function
    replaces the native annotation with `Annotated[native_annotation, Field(default_factory=__ddd__)]`
    https://pydantic-docs.helpmanual.io/usage/validation_decorator/#using-field-to-describe-function-arguments
    """
    __ddd__ = lambda: ...

    parameters = inspect.signature(procedure).parameters
    for p in parameters.values():
        if not p.default is ... or get_origin(p.annotation) is Annotated:
            continue

        annotation = p.annotation
        if annotation is inspect._empty:
            annotation = Any

        procedure.__annotations__[p.name] = Annotated[annotation, Field(default_factory=__ddd__)]

