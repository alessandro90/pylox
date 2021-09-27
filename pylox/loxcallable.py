from typing import Any, Protocol, runtime_checkable
import expr as e
import stmt as s
from environment import Environment


class CallableVisitor(Protocol):
    def visit_call_expr(self, expr: e.Call) -> Any:
        """Method used to interact with a Call expression object."""

    def get_globals(self) -> Environment:
        """Return the environment containing the globals of the interpreter."""

    def execute_block(self, statements: list[s.Stmt], env: Environment) -> None:
        """Execute a block of code."""


@runtime_checkable
class LoxCallable(Protocol):
    def call(self, interpreter: CallableVisitor, arguments: list[Any]) -> Any:
        """Method to actually invoke the function object."""

    def arity(self) -> int:
        """Return the arity of the function object."""


class LoxFunction:
    def __init__(self, declaration: s.Function):
        self._declaration = declaration

    def call(self, interpreter: CallableVisitor, arguments: list[Any]) -> None:
        env = Environment.nest(interpreter.get_globals())
        for par, arg in zip(self._declaration.params, arguments):
            env.define(par.lexeme, arg)

        interpreter.execute_block(self._declaration.body, env)
        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def __repr__(self) -> str:
        return f"<fn {self._declaration.name.lexeme} >"
