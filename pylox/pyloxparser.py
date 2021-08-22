from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Iterator, Optional, Callable, Any
from pyloxtoken import Token, TokenType
import expr as e
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

    def parse(self) -> Optional[e.Expr]:
        try:
            return self._expression()
        except ParserError as e:
            report({"Parse error:": e})
            return None

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

    def _check(self, token_type: TokenType) -> bool:
        return self._current.token_type == token_type

    def _check_or_raise(self, token_type: TokenType, message: str) -> bool:
        if not self._check(token_type):
            report(asdict(self._current), message)
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

    def _find_primary(self, tokens: dict[TokenType, Any]) -> Optional[e.Expr]:
        for token, literal in tokens.items():
            if self._match(token):
                ret = e.Literal(literal)
                self._current = self._try_get_next()
                return ret
        return None

    def _primary(self) -> e.Expr:
        primary_expression = self._find_primary(
            {
                TokenType.FALSE: False,
                TokenType.TRUE: True,
                TokenType.NIL: None,
                TokenType.NUMBER: self._current.literal,
                TokenType.STRING: self._current.literal,
            }
        )
        if primary_expression is not None:
            return primary_expression

        if self._match(TokenType.LEFT_PAREN):
            self._current = self._try_get_next()
            expression = self._expression()
            if self._check_or_raise(
                TokenType.RIGHT_PAREN, "Expect ')' after expression."
            ):
                self._current = self._try_get_next()

            return e.Grouping(expression)
        raise InternalPyloxError(
            f"Internal error: Invalid primary expression in {__file__}"
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
