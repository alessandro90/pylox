from typing import Any, Union
import expr as e
from pyloxtoken import TokenType
from numbers import Number
from exceptions import InternalPyloxError, PyloxRuntimeError


Value = Union[None, Number, str, bool]


def as_boolean(val: Any):
    """Return False if val is None or val is False.
    Return True otherwise."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return True


def assertNumberOperands(operator: TokenType, *operands: Value) -> None:
    if all(isinstance(operand, Number) for operand in operands):
        return
    raise PyloxRuntimeError(
        operator, f"Operand{'s' if len(operands) > 1 else ''} must be numeric."
    )


# TODO:
def pylox_stringify() -> str:
    pass


class Interpreter:
    def interpret(self, expr: e.Expr):
        try:
            value = self._evaluate(expr)
            print(pylox_stringify(value))
        except PyloxRuntimeError as e:
            print(e)

    def visit_literal_expr(self, expr: e.Literal) -> Value:
        return expr.value

    def visit_grouping_expr(self, expr: e.Grouping) -> Value:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: e.Unary) -> Value:
        right = self._evaluate(expr.right)
        if expr.operator == TokenType.MINUS:
            assertNumberOperands(expr.operator, right)
            return -right
        if expr.operator == TokenType.BANG:
            return not as_boolean(right)

    def visit_binary_expr(self, expr: e.Binary) -> Value:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        if expr.operator == TokenType.MINUS:
            assertNumberOperands(expr.operator, left, right)
            return left - right
        if expr.operator == TokenType.PLUS:
            if (isinstance(left, str) and isinstance(right, str)) or (
                isinstance(left, Number) and isinstance(right, Number)
            ):
                return left + right
            else:
                PyloxRuntimeError(
                    expr.operator,
                    "Operands must be two numbers or two strings.",
                )
        if expr.operator == TokenType.STAR:
            assertNumberOperands(expr.operator, left, right)
            return left * right
        if expr.operator == TokenType.SLASH:
            assertNumberOperands(expr.operator, left, right)
            return left / right
        if expr.operator == TokenType.GREATER:
            assertNumberOperands(expr.operator, left, right)
            return left > right
        if expr.operator == TokenType.GREATER_EQUAL:
            assertNumberOperands(expr.operator, left, right)
            return left >= right
        if expr.operator == TokenType.LESS:
            assertNumberOperands(expr.operator, left, right)
            return left < right
        if expr.operator == TokenType.LESS_EQUAL:
            assertNumberOperands(expr.operator, left, right)
            return left <= right
        if expr.operator == TokenType.EQUAL_EQUAL:
            return left == right
        if expr.operator == TokenType.BANG_EQUAL:
            return left != right
        raise InternalPyloxError(
            f"Invalid binary operator: {expr.operator.lexeme}"
        )

    def _evaluate(self, expression: e.Expr) -> Value:
        return expression.accept(self)
