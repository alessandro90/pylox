from typing import Any, NamedTuple, Optional
import sys


def _print_error(*args: Any, **kwargs: Any) -> None:
    """Utility function that redirects to standard error"""
    print(*args, file=sys.stderr, **kwargs)


class ErrorData(NamedTuple):
    line: int
    where: Optional[str]
    message: str


class ErrorInfo:
    """Encapsulates error information"""

    def __init__(self):
        self._errors: list[ErrorData] = []

    def push(self, err: ErrorData) -> None:
        self._errors.append(err)

    def has_error(self) -> bool:
        return len(self._errors) > 0

    def display(self) -> None:
        """Report an error on console"""
        self._report()

    def _report(self) -> None:
        """Utility function that register where the problem is"""
        for e in self._errors:
            _print_error(f"[line {e.line}] Error {e.where}: {e.message}")
