import stmt as s
import expr as e
from pyloxtoken import Token
from utils.error_handler import report
from typing import Protocol
from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Interpreter(Protocol):
    def resolve(self, expr: e.Expr, depth: int) -> None:
        """Resolves the number of environments between the use of a variable
        and its definition."""


class Resolver:
    def __init__(self, interpreter: Interpreter):
        self._interpreter = interpreter
        self._scopes: list[dict[str, bool]] = []
        self._current_function = FunctionType.NONE
        self._has_error = False

    def resolve_statements(self, statements: list[s.Stmt]) -> bool:
        self._resolve(statements)
        return not self._has_error

    def visit_block_stmt(self, stmt: s.Block):
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

    def visit_var_stmt(self, stmt: s.Var):
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_variable_expr(self, expr: e.Variable):
        in_scope = self._scopes[-1].get(expr.name.lexeme)
        if len(self._scopes) > 0 and in_scope is False:
            report(
                {"Error at line": expr.name.line, "Token": expr.name.lexeme},
                "Can't read local variable in its own initializer.",
            )
            self._has_error = True
        self._resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: e.Assign):
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: s.Function):
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt: s.Expression):
        self._resolve(stmt.expression)

    def visit_if_stmt(self, stmt: s.If):
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: s.Print):
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: s.Return):
        if self._current_function is FunctionType.NONE:
            report(
                {"Error:": stmt.keyword},
                "Can't return from top-level code.",
            )
            self._has_error = True
        if stmt.value is not None:
            self._resolve(stmt.value)

    def visit_while_stmt(self, stmt: s.While):
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_binary_expr(self, expr: e.Binary):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: e.Call):
        self._resolve(expr.callee)
        for argument in expr.arguments:
            self._resolve(argument)

    def visit_grouping_expr(self, expr: e.Grouping):
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr: e.Literal):
        pass

    def visit_logical_expr(self, expr: e.Logical):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary_expr(self, expr: e.Unary):
        self._resolve(expr.right)

    def visit_get_expr(self, expr: e.Get):
        pass

    def visit_set_expr(self, expr: e.Set):
        pass

    def visit_super_expr(self, expr: e.Super):
        pass

    def visit_this_expr(self, expr: e.This):
        pass

    def _resolve(self, statements: list[s.Stmt] | s.Stmt | e.Expr):
        match statements:
            case [*stmts]:  # noqa(E211)
                for statement in stmts:  # noqa(F821)
                    self._resolve(statement)
            case s.Stmt() | e.Expr():
                statements.accept(self)

    def _begin_scope(self):
        self._scopes.append({})

    def _end_scope(self):
        self._scopes.pop()

    def _declare(self, name: Token):
        if len(self._scopes) == 0:
            return
        if name.lexeme in self._scopes[-1]:
            report(
                {"Error: ": name.lexeme},
                "Already a variable with this name in this scope.",
            )
            self._has_error = True
        self._scopes[-1][name.lexeme] = False

    def _define(self, name: Token):
        if len(self._scopes) == 0:
            return
        self._scopes[-1][name.lexeme] = True

    def _resolve_local(self, expr: e.Expr, name: Token):
        for i, scope in enumerate(reversed(self._scopes)):
            if scope.get(name.lexeme) is not None:
                self._interpreter.resolve(expr, i)
                return

    def _resolve_function(
        self, function: s.Function, function_type: FunctionType
    ):
        enclosing_function = self._current_function
        self._current_function = function_type
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self._resolve(function.body)
        self._end_scope()
        self._current_function = enclosing_function
