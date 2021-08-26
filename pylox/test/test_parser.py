import expr as e
from pyloxtoken import Token, TokenType
from pyloxparser import Parser
from exceptions import ScannerError, InternalPyloxError
import pytest

# To simplify a bit, I'm going to compare expression
# by their string representation
from visitors import Stringyfier


def test_binary_expr():
    expression = e.Binary(
        e.Literal(5), Token(TokenType.PLUS, "+", None, 0), e.Literal(10)
    )
    expected = Stringyfier().stringify(expression)
    tokens = [
        Token(TokenType.NUMBER, "5", 5, 0),
        Token(TokenType.PLUS, "+", None, 0),
        Token(TokenType.NUMBER, "10", 10, 0),
        Token(TokenType.EOF, "", None, 0),
    ]
    parsed = Parser(iter(tokens)).parse()
    assert expected == Stringyfier().stringify(parsed)


def test_nested_expr():
    expression = e.Unary(
        Token(TokenType.BANG, "!", None, 0),
        e.Grouping(
            e.Binary(
                e.Literal(7),
                Token(TokenType.EQUAL_EQUAL, "==", None, 0),
                e.Literal(15),
            ),
        ),
    )
    expected = Stringyfier().stringify(expression)
    tokens = [
        Token(TokenType.BANG, "!", None, 0),
        Token(TokenType.LEFT_PAREN, "(", None, 0),
        Token(TokenType.NUMBER, "7", 7, 0),
        Token(TokenType.EQUAL_EQUAL, "==", None, 0),
        Token(TokenType.NUMBER, "15", 15, 0),
        Token(TokenType.RIGHT_PAREN, ")", None, 0),
        Token(TokenType.EOF, "", None, 0),
    ]
    parsed = Parser(iter(tokens)).parse()
    assert expected == Stringyfier().stringify(parsed)


def test_complex_expression():
    expression = e.Unary(
        Token(TokenType.MINUS, "-", None, 0),
        e.Grouping(
            e.Binary(
                e.Binary(
                    e.Grouping(
                        e.Binary(
                            e.Literal(5),
                            Token(TokenType.STAR, "*", None, 0),
                            e.Literal("s"),
                        )
                    ),
                    Token(TokenType.SLASH, "/", None, 0),
                    e.Unary(
                        Token(TokenType.BANG, "!", None, 0), e.Literal(True)
                    ),
                ),
                Token(TokenType.PLUS, "+", None, 0),
                e.Literal(None),
            ),
        ),
    )

    expected = Stringyfier().stringify(expression)

    tokens = [
        Token(TokenType.MINUS, "-", None, 0),
        Token(TokenType.LEFT_PAREN, "(", None, 0),
        Token(TokenType.LEFT_PAREN, "(", None, 0),
        Token(TokenType.NUMBER, "5", 5, 0),
        Token(TokenType.STAR, "*", None, 0),
        Token(TokenType.STRING, "s", "s", 0),
        Token(TokenType.RIGHT_PAREN, ")", None, 0),
        Token(TokenType.SLASH, "/", None, 0),
        Token(TokenType.BANG, "!", None, 0),
        Token(TokenType.TRUE, "true", True, 0),
        Token(TokenType.PLUS, "+", None, 0),
        Token(TokenType.NIL, "nil", None, 0),
        Token(TokenType.RIGHT_PAREN, ")", None, 0),
        Token(TokenType.EOF, "", None, 0),
    ]

    parsed = Parser(iter(tokens)).parse()
    assert expected == Stringyfier().stringify(parsed)


def test_error_after_scanner_error():
    def tokens():
        yield Token(TokenType.NUMBER, "1", 1, 0)
        raise ScannerError()

    assert Parser(tokens()).parse() is None


def test_error_stop_iteration():
    def tokens():
        yield Token(TokenType.NUMBER, "1", 1, 0)

    with pytest.raises(InternalPyloxError):
        _ = Parser(tokens()).parse()


def test_error_missing_paren():
    def tokens():
        yield Token(TokenType.LEFT_BRACE, "(", None, 0)
        yield Token(TokenType.NUMBER, "9", 9, 0)
        yield Token(TokenType.PLUS, "+", None, 0)
        yield Token(TokenType.NUMBER, "8", 8, 0)

    assert Parser(tokens()).parse() is None
