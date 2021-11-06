from __future__ import annotations
from typing import Any, Protocol, runtime_checkable
import expr as e
import stmt as s
from environment import Environment
from exceptions import Return, PyloxRuntimeError
from pyloxtoken import Token


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
    def __init__(
        self,
        declaration: s.Function,
        closure: Environment,
        is_initializer: bool,
    ):
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def call(self, interpreter: CallableVisitor, arguments: list[Any]) -> Any:
        env = Environment.nest(self._closure)
        for par, arg in zip(self._declaration.params, arguments):
            env.define(par.lexeme, arg)

        try:
            interpreter.execute_block(self._declaration.body, env)
        except Return as r:
            if self._is_initializer:
                return self._closure.get_at(0, "this")
            return r.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")
        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def bind(self, instance: LoxInstance) -> LoxFunction:
        env = Environment.nest(self._closure)
        env.define("this", instance)
        return LoxFunction(self._declaration, env, self._is_initializer)

    def __repr__(self) -> str:
        return f"<function {self._declaration.name.lexeme}>"


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self._klass = klass
        self._fields: dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        notFound = object()  # Use this to allow 'None' in the dictionary
        if (value := self._fields.get(name.lexeme, notFound)) is not notFound:
            return value
        method = self._klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise PyloxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self._fields[name.lexeme] = value

    def __repr__(self) -> str:
        return f"{self._klass._name} instance"


class LoxClass:
    def __init__(self, name: str, methods: dict[str, LoxFunction]):
        self._name = name
        self._methods = methods

    def call(
        self, interpreter: CallableVisitor, arguments: list[Any]
    ) -> LoxInstance:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        return self._methods.get(name)

    def arity(self) -> int:
        initializer = self.find_method("init")
        return 0 if initializer is None else initializer.arity()

    def __repr__(self) -> str:
        return f"<class {self._name} >"
