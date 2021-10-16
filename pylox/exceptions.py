from pyloxtoken import Token
from typing import Any


class InternalPyloxError(Exception):
    pass


class ParserError(Exception):
    pass


class ScannerError(Exception):
    pass


class PyloxRuntimeError(Exception):
    def __init__(self, token: Token, msg: str):
        super().__init__(msg)
        self.token = token


class PyloxDivisionByZeroError(PyloxRuntimeError):
    pass


class Return(Exception):
    def __init__(self, value: Any):
        self.value = value
