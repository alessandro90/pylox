from typing import Any
from time import time
from loxcallable import CallableVisitor


class Clock:
    """A clock class to get time elapsed between calls."""

    def arity(self) -> int:
        return 0

    def call(self, visitor: CallableVisitor, arguments: list[Any]) -> float:
        return time()

    def __repr__(self) -> str:
        return "<native fn>"
