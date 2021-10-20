from typing import Any, Type
import expr as e
import stmt as s
from pyloxtoken import TokenType, Token
from numbers import Number
from exceptions import (
    InternalPyloxError,
    PyloxRuntimeError,
    PyloxDivisionByZeroError,
    Return,
)
from utils.error_handler import report
from environment import Environment
from loxcallable import LoxCallable, LoxFunction
from native import Clock


def as_boolean(val: Any):
    """Return False if val is None or val is False.
    Return True otherwise."""
    match val:
        case bool():
            return val
        case None:
            return False
        case _:
            return True


def assertOperandsType(
    operator: Token, types: list[Type[Any]], *operands: Any
) -> None:
    for t in types:
        if all(isinstance(operand, t) for operand in operands):
            return
    raise PyloxRuntimeError(
        operator,
        f"Operand{'s' if len(operands) > 1 else ''} must be"
        f" {' or '.join(t.__name__ for t in types)}."
        f"{[repr(op) for op in operands]}",
    )


def pylox_stringify(value: Any) -> str:
    match value:
        case None:
            return "nil"
        case Number():
            return str(value).removesuffix(".0")
        case _:
            return str(value)


class Interpreter:
    def __init__(self):
        self._isrepl = False
        self._globals = Environment()
        self._environemnt = self._globals
        self._locals: dict[e.Expr, int] = {}

        self._globals.define("clock", Clock())

    def get_globals(self) -> Environment:
        return self._globals

    def set_repl(self) -> None:
        self._isrepl = True

    def interpret(self, statements: list[s.Stmt]) -> bool:
        try:
            for statement in statements:
                self._execute(statement)
            return True
        except PyloxRuntimeError as e:
            report({f"{e}": f"\n\t[line {e.token.line}]"})
            return False

    def resolve(self, expr: e.Expr, depth: int) -> None:
        self._locals[expr] = depth

    def _execute(self, statement: s.Stmt) -> None:
        statement.accept(self)

    def visit_expression_stmt(self, stmt: s.Expression) -> None:
        val = self._evaluate(stmt.expression)
        if self._isrepl:
            print(pylox_stringify(val))

    def visit_print_stmt(self, stmt: s.Print) -> None:
        value = self._evaluate(stmt.expression)
        print(pylox_stringify(value))

    def visit_var_stmt(self, stmt: s.Var) -> None:
        if stmt.initializer is None:
            value = None
        else:
            value = self._evaluate(stmt.initializer)
        self._environemnt.define(stmt.name.lexeme, value)

    def visit_block_stmt(self, stmt: s.Block) -> None:
        self.execute_block(stmt.statements, Environment.nest(self._environemnt))
        return None

    def visit_if_stmt(self, stmt: s.If) -> None:
        if as_boolean(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
        return None

    def visit_while_stmt(self, stmt: s.While) -> None:
        while as_boolean(self._evaluate(stmt.condition)):
            self._execute(stmt.body)
        return None

    def execute_block(self, statements: list[s.Stmt], env: Environment) -> None:
        prev = self._environemnt
        try:
            self._environemnt = env
            for statement in statements:
                self._execute(statement)
        except PyloxRuntimeError:
            raise
        finally:
            self._environemnt = prev

    def visit_literal_expr(self, expr: e.Literal) -> Any:
        return expr.value

    def visit_grouping_expr(self, expr: e.Grouping) -> Any:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: e.Unary) -> Any:
        right = self._evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                assertOperandsType(expr.operator, [Number], right)
                return -right  # type: ignore
            case TokenType.BANG:
                return not as_boolean(right)
        raise InternalPyloxError(
            f"Invalid unary expression {expr.operator.token_type}"
        )

    def visit_binary_expr(self, expr: e.Binary) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                assertOperandsType(expr.operator, [Number], left, right)
                return left - right  # type: ignore
            case TokenType.PLUS:
                assertOperandsType(expr.operator, [Number, str], left, right)
                return left + right  # type: ignore
            case TokenType.STAR:
                assertOperandsType(expr.operator, [Number], left, right)
                return left * right  # type: ignore
            case TokenType.SLASH:
                assertOperandsType(expr.operator, [Number], left, right)
                if right == 0:
                    raise PyloxDivisionByZeroError(
                        expr.operator, "Division by zero."
                    )
                return left / right  # type: ignore
            case TokenType.GREATER:
                assertOperandsType(expr.operator, [Number], left, right)
                return left > right  # type: ignore
            case TokenType.GREATER_EQUAL:
                assertOperandsType(expr.operator, [Number], left, right)
                return left >= right  # type: ignore
            case TokenType.LESS:
                assertOperandsType(expr.operator, [Number], left, right)
                return left < right  # type: ignore
            case TokenType.LESS_EQUAL:
                assertOperandsType(expr.operator, [Number], left, right)
                return left <= right  # type: ignore
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.BANG_EQUAL:
                return left != right
        raise InternalPyloxError(
            f"Invalid binary operator: {expr.operator.lexeme}"
        )

    def _evaluate(self, expression: e.Expr) -> Any:
        return expression.accept(self)

    def visit_assign_expr(self, expr: e.Assign) -> Any:
        value = self._evaluate(expr.value)
        if (distance := self._locals.get(expr)) is not None:
            self._environemnt.assign_at(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr: e.Call) -> Any:
        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise PyloxRuntimeError(
                expr.paren, "Can only call functions and classes."
            )
        if len(arguments) != callee.arity():
            raise PyloxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments"
                f"but got {len(arguments)} instead.",
            )
        return callee.call(self, arguments)

    def visit_get_expr(self, expr: e.Get) -> Any:
        ...

    def visit_logical_expr(self, expr: e.Logical) -> Any:
        left = self._evaluate(expr.left)
        truthy = as_boolean(left)
        if expr.operator.token_type is TokenType.OR:
            if truthy:
                return left
        else:  # AND
            if not truthy:
                return left
        return self._evaluate(expr.right)

    def visit_set_expr(self, expr: e.Set) -> Any:
        ...

    def visit_super_expr(self, expr: e.Super) -> Any:
        ...

    def visit_this_expr(self, expr: e.This) -> Any:
        ...

    def visit_variable_expr(self, expr: e.Variable) -> Any:
        return self._look_up_variable(expr.name, expr)

    def _look_up_variable(self, name: Token, expr: e.Variable):
        if (distance := self._locals.get(expr)) is not None:
            return self._environemnt.get_at(distance, name.lexeme)
        return self._globals.get(name)

    def visit_function_stmt(self, stmt: s.Function) -> None:
        function = LoxFunction(stmt, self._environemnt)
        self._environemnt.define(stmt.name.lexeme, function)
        return None

    def visit_return_stmt(self, stmt: s.Return) -> None:
        value: Any | None = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        raise Return(value)
