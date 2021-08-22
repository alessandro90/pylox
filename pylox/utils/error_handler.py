# from pyloxtoken import Token, TokenType
from typing import Any, Optional
from dataclasses import dataclass

import sys


def _print_error(*args: Any, **kwargs: Any) -> None:
    """Utility function that redirects to standard error"""
    print(*args, file=sys.stderr, **kwargs)


@dataclass(frozen=True)
class ErrorData:
    line: int
    where: Optional[str]
    message: str


def report(data: dict[Any, Any], message: Optional[str] = None) -> None:
    str_data = "".join([f"{k}: {v}" for k, v in data.items() if v is not None])
    if message is not None:
        _print_error(str_data, message)
    else:
        _print_error(str_data)


# class ErrorInfo:
#     """Encapsulates error information"""

#     def __init__(self):
#         self._errors: list[ErrorData] = []

#     def push(self, err: ErrorData) -> None:
#         self._errors.append(err)

#     def has_error(self) -> bool:
#         return len(self._errors) > 0

#     def display(self) -> None:
#         """Report an error on console"""
#         self._report()

#     def _report(self) -> None:
#         """Utility function that register where the problem is"""
#         for e in self._errors:
#             _print_error(f"[line {e.line}] Error {e.where}: {e.message}")

# def error(self, token: Token, message: str) -> None:
#     if token.type == TokenType.EOF:
#         self._report(token.line, " at end", message)
#     else:
#         self._report(token.line, " at '" + token.lexeme + "'", message)
