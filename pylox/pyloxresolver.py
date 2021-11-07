import stmt as s
import expr as e
from pyloxtoken import Token
from error_handler import report
from typing import Protocol, Any
from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Interpreter(Protocol):
    def resolve(self, expr: e.Expr, depth: int) -> None:
        """Resolves the number of environments between the use of a variable
        and its definition."""


class Resolver:
    def __init__(self, interpreter: Interpreter):
        self._interpreter = interpreter
        self._scopes: list[dict[str, bool]] = []
        self._current_function = FunctionType.NONE
        self._current_class = ClassType.NONE
        self._has_error = False

    def resolve_statements(self, statements: list[s.Stmt]) -> bool:
        self._resolve(statements)
        return not self._has_error

    def visit_block_stmt(self, stmt: s.Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

    def visit_class_stmt(self, stmt: s.Class) -> None:
        enclosing_class = self._current_class
        self._declare(stmt.name)
        self._define(stmt.name)
        if stmt.superclass is not None:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                self._report_error(
                    {"Error": stmt.superclass.name},
                    "A class cannot inherit from itself."
                )
            self._current_class = ClassType.SUBCLASS
            self._resolve(stmt.superclass)
            self._begin_scope()
            self._scopes[-1]["super"] = True
        else:
            self._current_class = ClassType.CLASS

        self._begin_scope()
        self._scopes[-1]["this"] = True
        for method in stmt.methods:
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            else:
                declaration = FunctionType.METHOD
            self._resolve_function(method, declaration)
        self._end_scope()
        if stmt.superclass is not None:
            self._end_scope()
        self._current_class = enclosing_class

    def visit_var_stmt(self, stmt: s.Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_variable_expr(self, expr: e.Variable) -> None:
        if self._scopes and self._scopes[-1].get(expr.name.lexeme) is False:
            self._report_error(
                {"Error at line": expr.name.line, "Token": expr.name.lexeme},
                "Can't read local variable in its own initializer.",
            )
        self._resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: e.Assign) -> None:
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: s.Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt: s.Expression) -> None:
        self._resolve(stmt.expression)

    def visit_if_stmt(self, stmt: s.If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: s.Print) -> None:
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: s.Return) -> None:
        def check_function_type(ftype: FunctionType, msg: str):
            if self._current_function is ftype:
                self._report_error({"Error:": stmt.keyword}, msg)

        check_function_type(
            FunctionType.NONE, "Can't return from top-level code."
        )
        if stmt.value is None:
            return None
        check_function_type(
            FunctionType.INITIALIZER,
            "Can't return a value from an initalizer."
        )
        self._resolve(stmt.value)

    def visit_while_stmt(self, stmt: s.While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_binary_expr(self, expr: e.Binary) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: e.Call) -> None:
        self._resolve(expr.callee)
        for argument in expr.arguments:
            self._resolve(argument)

    def visit_grouping_expr(self, expr: e.Grouping) -> None:
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr: e.Literal) -> None:
        pass

    def visit_logical_expr(self, expr: e.Logical) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary_expr(self, expr: e.Unary) -> None:
        self._resolve(expr.right)

    def visit_get_expr(self, expr: e.Get) -> None:
        self._resolve(expr.obj)

    def visit_set_expr(self, expr: e.Set) -> None:
        self._resolve(expr.value)
        self._resolve(expr.obj)

    def visit_super_expr(self, expr: e.Super) -> None:
        match self._current_class:
            case ClassType.NONE:
                self._report_error(
                    {"Error": expr.keyword},
                    "Cannot use 'super' outside of a class."
                )
            case ClassType.CLASS:
                self._report_error(
                    {"Error": expr.keyword},
                    "Cannot use 'super' in class with no superclass."
                )

        self._resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: e.This) -> None:
        if self._current_class is not ClassType.CLASS:
            self._report_error(
                {"Error: ": expr.keyword},
                "Cannot use 'this' outside of a class.",
            )
        self._resolve_local(expr, expr.keyword)

    def _report_error(
        self,
        data: dict[Any, Any],
        message: str | None = None
    ) -> None:
        self._has_error = True
        report(data, message)

    def _resolve(self, statements: list[s.Stmt] | s.Stmt | e.Expr) -> None:
        match statements:
            case [*stmts]:  # noqa(E211)
                for statement in stmts:  # noqa(F821)
                    self._resolve(statement)
            case s.Stmt() | e.Expr():
                statements.accept(self)

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if not self._scopes:
            return
        if name.lexeme in self._scopes[-1]:
            self._report_error(
                {"Error: ": name.lexeme},
                "Already a variable with this name in this scope.",
            )
        self._scopes[-1][name.lexeme] = False

    def _define(self, name: Token) -> None:
        if not self._scopes:
            return
        self._scopes[-1][name.lexeme] = True

    def _resolve_local(self, expr: e.Expr, name: Token) -> None:
        for i, scope in enumerate(reversed(self._scopes)):
            if scope.get(name.lexeme) is not None:
                self._interpreter.resolve(expr, i)
                return

    def _resolve_function(
        self, function: s.Function, function_type: FunctionType
    ) -> None:
        enclosing_function = self._current_function
        self._current_function = function_type
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self._resolve(function.body)
        self._end_scope()
        self._current_function = enclosing_function
