import expr as e
from pyloxtoken import Token, TokenType
from pyloxparser import Parser
from typing import Any


class ToList:
    def to_tuple(self, expr: e.Expr) -> list[Any]:
        return expr.accept(self)

    def visitAssignExpr(self, expr: e.Assign) -> list[Any]:
        return [expr.name, expr.value]

    def visitBinaryExpr(self, expr: e.Binary) -> list[Any]:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitCallExpr(self, expr: e.Call) -> list[Any]:
        ...

    def visitGetExpr(self, expr: e.Get) -> list[Any]:
        ...

    def visitGroupingExpr(self, expr: e.Grouping) -> list[Any]:
        return self._parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: e.Literal) -> list[Any]:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitLogicalExpr(self, expr: e.Logical) -> list[Any]:
        ...

    def visitSetExpr(self, expr: e.Set) -> list[Any]:
        ...

    def visitSuperExpr(self, expr: e.Super) -> list[Any]:
        ...

    def visitThisExpr(self, expr: e.This) -> list[Any]:
        ...

    def visitUnaryExpr(self, expr: e.Unary) -> list[Any]:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visitVariableExpr(self, expr: e.Variable) -> list[Any]:
        ...

    def _parenthesize(self, name: str, *expressions: e.Expr) -> list[Any]:
        text = f"({name}"
        for expression in expressions:
            text += f" {expression.accept(self)}"

        text += ")"
        return text


def compare_token(tka: Token, tkb: Token):
    return False


# What about using Stringyfier and just compare strings?
def compare_ast(a: e.Expr, b: e.Expr):
    if type(a) != type(b):
        return False
    # for av, bv in zip(a.__dict__.values(), b.__dict__.values()):
    #     if type(av) ==


# def test_dummy():
#     a = e.Binary(
#         e.Literal(5), Token(TokenType.PLUS, "+", None, 0), e.Literal(10)
#     )
#     b = e.Unary(Token(TokenType.BANG, "!", None, 0), e.Literal(None))
#     compare_ast(a, b)
#     assert compare_ast(a.b)
