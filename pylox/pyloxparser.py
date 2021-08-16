from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Iterator, Optional, Callable
from pyloxtoken import Token, TokenType
import expr as e
from exceptions import InternalPyloxError, ParserError


class Parser:
    def __init__(self, tokens: Iterator[Optional[Token]]):
        self._tokens = tokens
        self._current = self._try_get_next()

    def parse(self) -> e.Expr:
        return self._expression()

    def _try_get_next(self) -> Token:
        try:
            while (token := next(self._tokens)) is None:
                pass
            return token
        except StopIteration:
            raise InternalPyloxError(
                f"Accessing non-existing token: {__file__}"
            )

    def _check(self, token_type: TokenType) -> bool:
        return self._current.token_type == token_type

    def _check_or_raise(self, token_type: TokenType, message: str) -> bool:
        if not self._check(token_type):
            raise ParserError(message)
        return True

    def _match(self, *token_types: TokenType) -> bool:
        return any(self._check(token_type) for token_type in token_types)

    def _is_at_end(self) -> bool:
        return self._check(TokenType.EOF)

    def _expression(self) -> e.Expr:
        return self._equality()

    def _binary_expr(
        self, op: Callable[[], e.Expr], *token_types: TokenType
    ) -> e.Expr:
        expression = op()
        while self._match(*token_types):
            operation = self._current
            self._current = self._try_get_next()
            right = op()
            expression = e.Binary(expression, operation, right)
        return expression

    def _equality(self) -> e.Expr:
        return self._binary_expr(
            self._comparison, TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL
        )

    def _comparison(self) -> e.Expr:
        return self._binary_expr(
            self._term,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        )

    def _term(self) -> e.Expr:
        return self._binary_expr(self._factor, TokenType.MINUS, TokenType.PLUS)

    def _factor(self) -> e.Expr:
        return self._binary_expr(self._unary, TokenType.SLASH, TokenType.STAR)

    def _unary(self) -> e.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operation = self._current
            self._current = self._try_get_next()
            right = self._unary()
            return e.Unary(operation, right)
        return self._primary()

    def _primary(self) -> e.Expr:
        if self._match(TokenType.FALSE):
            self._current = self._try_get_next()
            return e.Literal(False)
        if self._match(TokenType.TRUE):
            self._current = self._try_get_next()
            return e.Literal(True)
        if self._match(TokenType.NIL):
            self._current = self._try_get_next()
            return e.Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            literal = e.Literal(self._current.literal)
            self._current = self._try_get_next()
            return literal

        if self._match(TokenType.LEFT_PAREN):
            self._current = self._try_get_next()
            expression = self._expression()
            if self._check_or_raise(
                TokenType.RIGHT_PAREN, "Expect ')' after expression."
            ):
                self._current = self._try_get_next()

            return e.Grouping(expression)
        raise InternalPyloxError(
            f"Internal error: Invalid promary expression in {__file__}"
        )
