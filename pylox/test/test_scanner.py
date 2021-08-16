from scanner import Scanner, TokenMatch
from source import Source
from pyloxtoken import Token, TokenType
from utils.error_handler import ErrorData
from unittest.mock import Mock


def test_scan_tokens_end():
    source = Source("")
    scanner = Scanner(source, [])
    assert next(scanner.scan_tokens()) == Token(
        TokenType.EOF, "", None, source.line()
    )


def test_scan_tokens_error():
    source = Source(".")
    scanner = Scanner(
        source, [lambda _, __: TokenMatch.error(ErrorData(0, None, "error"))]
    )
    assert next(scanner.scan_tokens()) is None
    assert scanner.error_info().has_error()


def test_scan_tokens_found_one():
    source = Source(".")
    token = Token.make(source, TokenType.AND, 10)
    scanner = Scanner(source, [lambda _, __: TokenMatch.found(token)])

    assert next(scanner.scan_tokens()) == token


def test_scan_tokens_multiple():
    mock_source = Mock(spec_set=Source)
    mock_source.is_at_end.return_value = False
    mock_source.advance.side_effect = ["{", "/", "."]
    mock_source.line.return_value = 1

    def make_token_finder(c, *, token_type, force_none=False, sink=False):
        def finder(char, source):
            if sink:
                return TokenMatch.found()
            if c != char:
                return TokenMatch.none()
            return (
                TokenMatch.found(Token.make(source, token_type))
                if not force_none
                else TokenMatch.found()
            )

        return finder

    token_finders = [
        make_token_finder("{", token_type=TokenType.LEFT_BRACE),
        make_token_finder("/", token_type=None, force_none=True),
        make_token_finder(None, token_type=None, sink=True),
    ]

    scanner = Scanner(mock_source, token_finders)
    tokens = scanner.scan_tokens()

    assert next(tokens) == Token.make(mock_source, TokenType.LEFT_BRACE)
    assert next(tokens) is None

    mock_source.is_at_end.return_value = True

    assert next(tokens) == Token(TokenType.EOF, "", None, mock_source.line())
