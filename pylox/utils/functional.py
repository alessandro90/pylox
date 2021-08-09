from typing import Callable, Optional, TypeVar

# Generics types
T = TypeVar("T")
Q = TypeVar("Q")


def opt_map(val: Optional[T], cb: Callable[[T], Q], default: Q) -> Q:
    """Return callable(var) if var is not None, otherwise return default"""
    if val is None:
        return default
    return cb(val)


def opt_map_or_false(val: Optional[T], cb: Callable[[T], bool]) -> bool:
    return opt_map(val, cb, False)
