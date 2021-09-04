from typing import Any, Union, Type
import expr as e
import stmt as s
from pyloxtoken import TokenType, Token
from numbers import Number
from exceptions import (
    InternalPyloxError,
    PyloxRuntimeError,
    PyloxDivisionByZeroError,
)
from utils.error_handler import report
from environment import Environment


Value = Union[None, Number, str, bool]


def as_boolean(val: Any):
    """Return False if val is None or val is False.
    Return True otherwise."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return True


def assertOperandsType(
    operator: Token, types: list[Type[Any]], *operands: Value
) -> None:
    for t in types:
        if all(isinstance(operand, t) for operand in operands):
            return
    raise PyloxRuntimeError(
        operator,
        f"Operand{'s' if len(operands) > 1 else ''} must be"
        f" {' or '.join(t.__name__ for t in types)}.",
    )


def pylox_stringify(value: Any) -> str:
    if value is None:
        return "nil"
    if isinstance(value, Number):
        text = str(value)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    return str(value)


class Interpreter:
    def __init__(self):
        self._environemnt = Environment()

    def interpret(self, statements: list[s.Stmt]) -> bool:
        try:
            for statement in statements:
                self._execute(statement)
            return True
        except PyloxRuntimeError as e:
            report({f"{e}": f"\n\t[line {e.token.line}]"})
            return False

    def _execute(self, statement: s.Stmt) -> None:
        statement.accept(self)

    def visit_expression_stmt(self, stmt: s.Expression) -> None:
        self._evaluate(stmt.expression)

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
        self._execute_block(
            stmt.statements, Environment.nest(self._environemnt)
        )
        return None

    def _execute_block(
        self, statements: list[s.Stmt], env: Environment
    ) -> None:
        prev = self._environemnt
        try:
            self._environemnt = env
            for statement in statements:
                self._execute(statement)
        except PyloxRuntimeError:
            pass
        finally:
            self._environemnt = prev

    def visit_literal_expr(self, expr: e.Literal) -> Value:
        return expr.value

    def visit_grouping_expr(self, expr: e.Grouping) -> Value:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: e.Unary) -> Value:
        right = self._evaluate(expr.right)
        if expr.operator.token_type == TokenType.MINUS:
            assertOperandsType(expr.operator, [Number], right)
            return -right  # type: ignore
        if expr.operator.token_type == TokenType.BANG:
            return not as_boolean(right)
        raise InternalPyloxError(
            f"Invalid unary expression {expr.operator.token_type}"
        )

    def visit_binary_expr(self, expr: e.Binary) -> Value:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        if expr.operator.token_type == TokenType.MINUS:
            assertOperandsType(expr.operator, [Number], left, right)
            return left - right  # type: ignore
        if expr.operator.token_type == TokenType.PLUS:
            assertOperandsType(expr.operator, [Number, str], left, right)
            return left + right  # type: ignore
        if expr.operator.token_type == TokenType.STAR:
            assertOperandsType(expr.operator, [Number], left, right)
            return left * right  # type: ignore
        if expr.operator.token_type == TokenType.SLASH:
            assertOperandsType(expr.operator, [Number], left, right)
            if right == 0:
                raise PyloxDivisionByZeroError(
                    expr.operator, "Division by zero."
                )
            return left / right  # type: ignore
        if expr.operator.token_type == TokenType.GREATER:
            assertOperandsType(expr.operator, [Number], left, right)
            return left > right  # type: ignore
        if expr.operator.token_type == TokenType.GREATER_EQUAL:
            assertOperandsType(expr.operator, [Number], left, right)
            return left >= right  # type: ignore
        if expr.operator.token_type == TokenType.LESS:
            assertOperandsType(expr.operator, [Number], left, right)
            return left < right  # type: ignore
        if expr.operator.token_type == TokenType.LESS_EQUAL:
            assertOperandsType(expr.operator, [Number], left, right)
            return left <= right  # type: ignore
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return left == right
        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return left != right
        raise InternalPyloxError(
            f"Invalid binary operator: {expr.operator.lexeme}"
        )

    def _evaluate(self, expression: e.Expr) -> Value:
        return expression.accept(self)

    def visit_assign_expr(self, expr: e.Assign) -> Value:
        value = self._evaluate(expr.value)
        self._environemnt.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr: e.Call) -> Value:
        ...

    def visit_get_expr(self, expr: e.Get) -> Value:
        ...

    def visit_logical_expr(self, expr: e.Logical) -> Value:
        ...

    def visit_set_expr(self, expr: e.Set) -> Value:
        ...

    def visit_super_expr(self, expr: e.Super) -> Value:
        ...

    def visit_this_expr(self, expr: e.This) -> Value:
        ...

    def visit_variable_expr(self, expr: e.Variable) -> Value:
        return self._environemnt.get(expr.name)
