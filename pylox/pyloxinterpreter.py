from typing import Any, Union, Callable
import expr as e
from pyloxtoken import TokenType, Token
from numbers import Number
from exceptions import InternalPyloxError, PyloxRuntimeError
from utils.error_handler import report

# import operator as op


Value = Union[None, Number, str, bool]


def as_boolean(val: Any):
    """Return False if val is None or val is False.
    Return True otherwise."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return True


def assertNumberOperands(operator: Token, *operands: Value) -> None:
    if not all(isinstance(operand, Number) for operand in operands):
        raise PyloxRuntimeError(
            operator,
            f"Operand{'s' if len(operands) > 1 else ''} must be numeric.",
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


# def interpret_expr(
#     assertion: Callable,
#     operation: Callable[..., Value],
#     operator: Token,
#     *operands: Value,
# ) -> Value:
#     assertion(operator, *operands)
#     return operation(*operands)


class Interpreter:
    def interpret(self, expr: e.Expr) -> bool:
        try:
            value = self._evaluate(expr)
            print(pylox_stringify(value))
            return True
        except PyloxRuntimeError as e:
            report({type(e): f"{e}\n[line {e.token.line}]"})
            return False

    def visit_literal_expr(self, expr: e.Literal) -> Value:
        return expr.value

    def visit_grouping_expr(self, expr: e.Grouping) -> Value:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: e.Unary) -> Value:
        right = self._evaluate(expr.right)
        if expr.operator.token_type == TokenType.MINUS:
            assertNumberOperands(expr.operator, right)
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
            assertNumberOperands(expr.operator, left, right)
            return left - right  # type: ignore
        if expr.operator.token_type == TokenType.PLUS:
            if (isinstance(left, str) and isinstance(right, str)) or (
                isinstance(left, Number) and isinstance(right, Number)
            ):
                return left + right  # type: ignore
            else:
                PyloxRuntimeError(
                    expr.operator,
                    "Operands must be two numbers or two strings.",
                )
        if expr.operator.token_type == TokenType.STAR:
            assertNumberOperands(expr.operator, left, right)
            return left * right  # type: ignore
        if expr.operator.token_type == TokenType.SLASH:
            assertNumberOperands(expr.operator, left, right)
            return left / right  # type: ignore
        if expr.operator.token_type == TokenType.GREATER:
            assertNumberOperands(expr.operator, left, right)
            return left > right  # type: ignore
        if expr.operator.token_type == TokenType.GREATER_EQUAL:
            assertNumberOperands(expr.operator, left, right)
            return left >= right  # type: ignore
        if expr.operator.token_type == TokenType.LESS:
            assertNumberOperands(expr.operator, left, right)
            return left < right  # type: ignore
        if expr.operator.token_type == TokenType.LESS_EQUAL:
            assertNumberOperands(expr.operator, left, right)
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
        ...

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
        ...
