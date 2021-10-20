from pyloxtoken import Token
from typing import Any
from abc import ABC


class BasePyloxErrro(ABC, Exception):
    pass


class InternalPyloxError(BasePyloxErrro):
    pass


class ParserError(BasePyloxErrro):
    pass


class ScannerError(BasePyloxErrro):
    pass


class PyloxRuntimeError(BasePyloxErrro):
    def __init__(self, token: Token, msg: str):
        super().__init__(msg)
        self.token = token


class PyloxDivisionByZeroError(PyloxRuntimeError):
    pass


class Return(BasePyloxErrro):
    def __init__(self, value: Any):
        self.value = value
