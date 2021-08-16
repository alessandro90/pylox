import expr as e


class Stringyfier:
    def stringify(self, expr: e.Expr) -> str:
        return expr.accept(self)

    def visitAssignExpr(self, expr: e.Assign) -> str:
        ...

    def visitBinaryExpr(self, expr: e.Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitCallExpr(self, expr: e.Call) -> str:
        ...

    def visitGetExpr(self, expr: e.Get) -> str:
        ...

    def visitGroupingExpr(self, expr: e.Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: e.Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitLogicalExpr(self, expr: e.Logical) -> str:
        ...

    def visitSetExpr(self, expr: e.Set) -> str:
        ...

    def visitSuperExpr(self, expr: e.Super) -> str:
        ...

    def visitThisExpr(self, expr: e.This) -> str:
        ...

    def visitUnaryExpr(self, expr: e.Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visitVariableExpr(self, expr: e.Variable) -> str:
        ...

    def _parenthesize(self, name: str, *expressions: e.Expr) -> str:
        text = f"({name}"
        for expression in expressions:
            text += f" {expression.accept(self)}"

        text += ")"
        return text
