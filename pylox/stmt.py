# This file is autogenerated from generator.py
# Do not manually change it.

from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Protocol, TypeVar, Optional
from pyloxtoken import Token
import expr as e


T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


class Visitor(Protocol[T_co]):
    def visit_block_stmt(self, stmt: Block) -> T_co:
        ...

    def visit_expression_stmt(self, stmt: Expression) -> T_co:
        ...

    def visit_if_stmt(self, stmt: If) -> T_co:
        ...

    def visit_print_stmt(self, stmt: Print) -> T_co:
        ...

    def visit_var_stmt(self, stmt: Var) -> T_co:
        ...

    def visit_while_stmt(self, stmt: While) -> T_co:
        ...


class Stmt(Protocol[T]):
    def accept(self, visitor: Visitor[T]) -> T:
        ...


class Block:
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_block_stmt(self)


class Expression:
    def __init__(self, expression: e.Expr):
        self.expression = expression

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_expression_stmt(self)


class If:
    def __init__(self, condition: e.Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_if_stmt(self)


class Print:
    def __init__(self, expression: e.Expr):
        self.expression = expression

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_print_stmt(self)


class Var:
    def __init__(self, name: Token, initializer: Optional[e.Expr]):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_var_stmt(self)


class While:
    def __init__(self, condition: e.Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: Visitor[T_co]) -> T_co:
        return visitor.visit_while_stmt(self)
