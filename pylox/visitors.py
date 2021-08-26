import expr as e


class Stringyfier:
    def stringify(self, expr: e.Expr) -> str:
        return expr.accept(self)

    def visit_assign_expr(self, expr: e.Assign) -> str:
        ...

    def visit_binary_expr(self, expr: e.Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr: e.Call) -> str:
        ...

    def visit_get_expr(self, expr: e.Get) -> str:
        ...

    def visit_grouping_expr(self, expr: e.Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: e.Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_logical_expr(self, expr: e.Logical) -> str:
        ...

    def visit_set_expr(self, expr: e.Set) -> str:
        ...

    def visit_super_expr(self, expr: e.Super) -> str:
        ...

    def visit_this_expr(self, expr: e.This) -> str:
        ...

    def visit_unary_expr(self, expr: e.Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: e.Variable) -> str:
        ...

    def _parenthesize(self, name: str, *expressions: e.Expr) -> str:
        text = f"({name}"
        for expression in expressions:
            text += f" {expression.accept(self)}"

        text += ")"
        return text
