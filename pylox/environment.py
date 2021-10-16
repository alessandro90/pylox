from __future__ import annotations  # NOTE: No need since python 3.11+
from typing import Any
from pyloxtoken import Token
from exceptions import PyloxRuntimeError


class Environment:
    def __init__(self):
        self._values: dict[str, Any] = {}
        self._enclosing: Environment | None = None

    @classmethod
    def nest(cls, enclosing: Environment) -> Environment:
        environemnt = Environment()
        environemnt._enclosing = enclosing
        return environemnt

    def define(self, name: str, value: Any):
        self._values[name] = value

    def get(self, name: Token) -> Any:
        if (value := self._values.get(name.lexeme, None)) is not None:
            return value
        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise PyloxRuntimeError(name, f'Undefined variable "{name.lexeme}"')

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return
        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return
        raise PyloxRuntimeError(name, f'Undefined variable "{name.lexeme}"')
