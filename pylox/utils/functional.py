from typing import Callable, Optional, TypeVar

# Generics types
T = TypeVar("T")
Q = TypeVar("Q")


def try_invoke(val: Optional[T], cb: Callable[[T], Q], default: Q) -> Q:
    """Return callable(var) if var is not None, otherwise return default"""
    if val is None:
        return default
    return cb(val)


def try_invoke_bool(val: Optional[T], cb: Callable[[T], bool]) -> bool:
    return try_invoke(val, cb, False)
