from typing import Any
from pyloxtoken import Token
from exceptions import PyloxRuntimeError


class Environment:
    def __init__(self):
        self._values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self._values[name] = value

    def get(self, name: Token) -> Any:
        try:
            return self._values[name.lexeme]
        except KeyError:
            raise PyloxRuntimeError(f"Undefined variable '{name.lexeme}'.")
