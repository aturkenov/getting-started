from typing import Callable, Mapping
from wampify import Wampify
from ..shared.make_ellipsis_default import make_ellipsis_default


def wampify_register(
    wampify_instance: Wampify,
    uri: str,
    procedure: Callable,
    options: Mapping = {}
):
    make_ellipsis_default(procedure)

    wampify_instance.add_register(
        uri, procedure, options
    )


def wampify_subscribe(
    wampify_instance: Wampify,
    uri: str,
    procedure: Callable,
    options: Mapping
):
    make_ellipsis_default(procedure)

    wampify_instance.add_subscribe(
        uri, procedure, options
    )

