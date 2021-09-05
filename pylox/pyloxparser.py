from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Iterator, Optional, Callable, Any, Type, Union
from pyloxtoken import Token, TokenType
import expr as e
import stmt as s
from exceptions import InternalPyloxError, ParserError, ScannerError
from utils.error_handler import report
from dataclasses import asdict

# TODO:
# challenge 2. ch. 6 "Parsing Expressions" => implement '?:' operator
# challenge 3. ch. 6 "Parsing Expressions" => error production for incomplete
# binary operator


class Parser:
    def __init__(self, tokens: Iterator[Optional[Token]]):
        self._tokens = tokens
        self._current = self._try_get_next()

    def parse(self) -> Optional[list[s.Stmt]]:
        statements = []
        has_error = False
        while not self._is_at_end():
            statement = self._statement()
            if statement is not None and not has_error:
                statements.append(statement)
            else:
                has_error = True
        if has_error:
            return None
        return statements

    def _declaration(self) -> Optional[s.Stmt]:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParserError as e:
            report({"Parse error": e})
            self._synchronize()
            return None

    def _var_declaration(self) -> s.Stmt:
        self._current = self._try_get_next()
        name = self._current
        self._current = self._get_next_if_current_is(
            TokenType.IDENTIFIER, "Expect variable name."
        )

        initializer: Optional[e.Expr] = None
        if self._match(TokenType.EQUAL):
            self._current = self._try_get_next()
            initializer = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after variable declaration"
        )
        return s.Var(name, initializer)

    def _statement(self) -> s.Stmt:
        if self._match(TokenType.IF):
            self._current = self._try_get_next()
            return self._if_statement()
        if self._match(TokenType.PRINT):
            self._current = self._try_get_next()
            return self._print_statement()
        if self._match(TokenType.LEFT_BRACE):
            self._current = self._try_get_next()
            return s.Block(self._block())
        return self._expression_statement()

    def _if_statement(self):
        self._current = self._get_next_if_current_is(
            TokenType.LEFT_PAREN, "Expect '(' after if."
        )
        condition = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_PAREN, "Expect ')' after if body."
        )
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return s.If(condition, then_branch, else_branch)

    def _block(self):
        statements = []
        while not self._match(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_BRACE, "Expect '}' after block."
        )
        return statements

    def _print_statement(self) -> s.Stmt:
        value = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after value."
        )
        return s.Print(value)

    def _expression_statement(self) -> s.Stmt:
        expression = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after expression."
        )
        return s.Expression(expression)

    def _try_get_next(self) -> Token:
        try:
            while (token := next(self._tokens)) is None:
                pass
            return token
        except ScannerError:
            raise ParserError("Parse error due to previous scanner error.")
        except StopIteration:
            raise InternalPyloxError(
                f"Accessing non-existing token: {__file__}"
            )

    def _get_next_if_current_is(
        self, token_type: TokenType, message: str
    ) -> Token:
        if not self._match(token_type):
            raise ParserError(self._current, message)
        return self._try_get_next()

    def _match(self, *token_types: TokenType) -> bool:
        return any(
            self._current.token_type == token_type for token_type in token_types
        )

    def _is_at_end(self) -> bool:
        return self._match(TokenType.EOF)

    def _expression(self) -> e.Expr:
        return self._assignment()

    def _assignment(self) -> e.Expr:
        expr = self._or()
        if self._match(TokenType.EQUAL):
            equals = self._current
            self._current = self._try_get_next()
            value = self._assignment()
            if isinstance(expr, e.Variable):
                return e.Assign(expr.name, value)

            report(asdict(equals), "Invalid assignement target.")

        return expr

    def _or(self) -> e.Expr:
        return self._binary_expr(self._and, [TokenType.OR], e.Logical)

    def _and(self):
        return self._binary_expr(self._equality, [TokenType.AND], e.Logical)

    def _binary_expr(
        self,
        op: Callable[[], e.Expr],
        token_types: list[TokenType],
        expr_class: Type[Union[e.Binary, e.Logical]] = e.Binary,
    ) -> e.Expr:
        expression = op()
        while self._match(*token_types):
            operation = self._current
            self._current = self._try_get_next()
            right = op()
            expression = expr_class(expression, operation, right)
        return expression

    def _equality(self) -> e.Expr:
        return self._binary_expr(
            self._comparison, [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
        )

    def _comparison(self) -> e.Expr:
        return self._binary_expr(
            self._term,
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ],
        )

    def _term(self) -> e.Expr:
        return self._binary_expr(
            self._factor, [TokenType.MINUS, TokenType.PLUS]
        )

    def _factor(self) -> e.Expr:
        return self._binary_expr(self._unary, [TokenType.SLASH, TokenType.STAR])

    def _unary(self) -> e.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operation = self._current
            self._current = self._try_get_next()
            right = self._unary()
            return e.Unary(operation, right)
        return self._primary()

    def _find_literal(self, tokens: dict[TokenType, Any]) -> Optional[e.Expr]:
        for token, literal in tokens.items():
            if self._match(token):
                ret = e.Literal(literal)
                self._current = self._try_get_next()
                return ret
        return None

    def _primary(self) -> e.Expr:
        if (
            primary_expression := self._find_literal(
                {
                    TokenType.FALSE: False,
                    TokenType.TRUE: True,
                    TokenType.NIL: None,
                    TokenType.NUMBER: self._current.literal,
                    TokenType.STRING: self._current.literal,
                }
            )
        ) is not None:
            return primary_expression

        if self._match(TokenType.IDENTIFIER):
            var = self._current
            self._current = self._try_get_next()
            return e.Variable(var)

        if self._match(TokenType.LEFT_PAREN):
            self._current = self._try_get_next()
            expression = self._expression()
            self._current = self._get_next_if_current_is(
                TokenType.RIGHT_PAREN, "Expect ')' after expression."
            )
            return e.Grouping(expression)

        raise ParserError(
            f"Invalid primary expression:\n"
            f"Line: {self._current.line}\n"
            f"Expression: {self._current.lexeme}"
        )

    def _synchronize(self) -> None:
        while not self._is_at_end():
            if self._current.token_type == TokenType.SEMICOLON:
                self._current = self._try_get_next()
                return
            if any(
                token == self._current.token_type
                for token in (
                    TokenType.CLASS,
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.FOR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN,
                )
            ):
                return
            self._current = self._try_get_next()
