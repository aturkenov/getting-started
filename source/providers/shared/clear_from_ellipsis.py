from typing import Mapping, Any


def clear_from_ellipsis(
    **kwargs: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Deletes all keys from dict where value is ellipsis(...), and it works recursively
    """
    kwargs_without_ellipsis = {}
    for key, value in kwargs.items():
        if value is ...:
            continue

        kwargs_without_ellipsis[key] = value

        if type(value) is dict:
            kwargs_without_ellipsis[key] = clear_from_ellipsis(**value)

    return kwargs_without_ellipsis
