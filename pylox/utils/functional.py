from typing import Callable, Optional, TypeVar

# Generics types
T = TypeVar("T")
Q = TypeVar("Q")


def try_invoke(
    val: Optional[T], callable: Callable[[T], Q], default: Optional[Q] = None
) -> Optional[Q]:
    """Return callable(var) if var is not None, otherwise return default"""
    if val is None:
        return default
    return callable(val)
