from __future__ import annotations  # NOTE: No need since python 3.11+
from typing import Any
from pyloxtoken import Token
from exceptions import PyloxRuntimeError


class Environment:
    def __init__(self):
        self._values: dict[str, Any] = {}
        self.enclosing: Environment | None = None

    @classmethod
    def nest(cls, enclosing: Environment) -> Environment:
        environemnt = Environment()
        environemnt.enclosing = enclosing
        return environemnt

    def define(self, name: str, value: Any):
        self._values[name] = value

    def get(self, name: Token) -> Any:
        if (value := self._values.get(name.lexeme)) is not None:
            return value
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise PyloxRuntimeError(name, f'Undefined variable "{name.lexeme}"')

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise PyloxRuntimeError(name, f'Undefined variable "{name.lexeme}"')

    def get_at(self, distance: int, name: str) -> Any:
        return self._ancestor(distance)._values.get(name)

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self._ancestor(distance)._values[name.lexeme] = value

    def _ancestor(self, distance: int) -> Environment:
        environment = self
        for _ in range(distance):
            assert (
                environment.enclosing is not None
            ), "Internal error: Invalid null scope."
            environment = environment.enclosing
        return environment
