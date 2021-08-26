# This file is autogenerated from expr_generator.py
# Do not manually change it.

from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Any, Protocol, TypeVar
from pyloxtoken import Token


T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


class Visitor(Protocol[T_co]):
    def visit_assign_expr(self, expr: Assign) -> T_co:
        ...

    def visit_binary_expr(self, expr: Binary) -> T_co:
        ...

    def visit_call_expr(self, expr: Call) -> T_co:
        ...

    def visit_get_expr(self, expr: Get) -> T_co:
        ...

    def visit_grouping_expr(self, expr: Grouping) -> T_co:
        ...

    def visit_literal_expr(self, expr: Literal) -> T_co:
        ...

    def visit_logical_expr(self, expr: Logical) -> T_co:
        ...

    def visit_set_expr(self, expr: Set) -> T_co:
        ...

    def visit_super_expr(self, expr: Super) -> T_co:
        ...

    def visit_this_expr(self, expr: This) -> T_co:
        ...

    def visit_unary_expr(self, expr: Unary) -> T_co:
        ...

    def visit_variable_expr(self, expr: Variable) -> T_co:
        ...


class Expr(Protocol[T]):
    def accept(self, visitor: Visitor[T]) -> T:
        ...


class Assign:
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_assign_expr(self)


class Binary:
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_binary_expr(self)


class Call:
    def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_call_expr(self)


class Get:
    def __init__(self, obj: Expr, name: Token):
        self.obj = obj
        self.name = name

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_get_expr(self)


class Grouping:
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_grouping_expr(self)


class Literal:
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_literal_expr(self)


class Logical:
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_logical_expr(self)


class Set:
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj = obj
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_set_expr(self)


class Super:
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_super_expr(self)


class This:
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_this_expr(self)


class Unary:
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_unary_expr(self)


class Variable:
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_variable_expr(self)
