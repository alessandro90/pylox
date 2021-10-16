from __future__ import annotations  # NOTE: No need since python 3.10+
from typing import Callable, Iterable, Optional, Iterator
from dataclasses import dataclass, asdict
from utils.error_handler import ErrorData, report
from utils.functional import opt_map_or_false
from pyloxtoken import Token, TokenType
from source import Source
from exceptions import ScannerError
from string import ascii_letters


RESERVED_KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class NotFound:
    """A sentinel object to indicate something is not found."""
    pass


TokenFinderResult = Optional[Token | ErrorData | NotFound]


@dataclass(frozen=True, eq=False)
class TokenMatch:
    """Wrapper to a result from a token_finder_* method"""

    result: TokenFinderResult

    @classmethod
    def none(cls) -> TokenMatch:
        return cls(result=NotFound())

    @classmethod
    def found(cls, res: Optional[Token] = None) -> TokenMatch:
        return cls(result=res)

    @classmethod
    def error(cls, err: ErrorData) -> TokenMatch:
        return cls(result=err)


def token_finder_single_char_factory(
    char: str, token_type: TokenType
) -> Callable[[str, Source], TokenMatch]:
    def token_finder_single_char(c: str, source: Source) -> TokenMatch:
        if c != char:
            return TokenMatch.none()
        return TokenMatch.found(Token.make(source, token_type))

    return token_finder_single_char


def token_finder_disambiguate_factory(
    char: str, next_char: str, token_type: TokenType, next_token_type: TokenType
) -> Callable[[str, Source], TokenMatch]:
    def token_finder_disambiguate(c: str, source: Source) -> TokenMatch:
        if c == char:
            if source.consume_next_if_is(next_char):
                return TokenMatch.found(Token.make(source, next_token_type))
            else:
                return TokenMatch.found(Token.make(source, token_type))
        else:
            return TokenMatch.none()

    return token_finder_disambiguate


def token_finder_slash_or_comment(c: str, source: Source) -> TokenMatch:
    if c != "/":
        return TokenMatch.none()
    if source.consume_next_if_is("/"):
        while opt_map_or_false(source.peek(), lambda x: x != "\n"):
            source.advance()
        return TokenMatch.found()
    elif source.consume_next_if_is("*"):
        while True:
            if source.is_at_end():
                return TokenMatch.error(
                    ErrorData(source.line(), None, "Untermined comment")
                )

            if (char := source.advance()) == "\n":
                source.newline()
            elif char == "*" and opt_map_or_false(
                source.peek(), lambda x: x == "/"
            ):
                source.advance()
                return TokenMatch.found()
    else:
        return TokenMatch.found(Token.make(source, TokenType.SLASH))


def token_finder_discard_factory(
    *to_discard: str,
) -> Callable[[str, Source], TokenMatch]:
    should_discard = lambda x: any(x == skip for skip in to_discard)

    def token_finder_discard(c: str, source: Source) -> TokenMatch:
        if should_discard(c):
            while opt_map_or_false(source.peek(), should_discard):
                source.advance()
            return TokenMatch.found()
        return TokenMatch.none()

    return token_finder_discard


def token_finder_newline(c: str, source: Source) -> TokenMatch:
    if c == "\n":
        source.newline()
        return TokenMatch.found()
    return TokenMatch.none()


def token_finder_string(c: str, source: Source) -> TokenMatch:
    if c != '"':
        return TokenMatch.none()

    while opt_map_or_false(char := source.peek(), lambda x: x != '"'):
        if char == "\n":
            source.newline()
        source.advance()
    if source.is_at_end():
        return TokenMatch.error(
            ErrorData(source.line(), None, "Untermined string")
        )
    else:
        source.advance()
        return TokenMatch.found(
            Token.make(source, TokenType.STRING, source.lexeme()[1:-1])
        )


def token_finder_number(c: str, source: Source) -> TokenMatch:
    if not c.isdigit():
        return TokenMatch.none()

    is_digit = lambda char: char.isdigit()

    while opt_map_or_false(source.peek(), is_digit):
        source.advance()

    if opt_map_or_false(
        source.peek(), lambda char: char == "."
    ) and opt_map_or_false(source.peek(1), is_digit):
        source.advance()

    while opt_map_or_false(source.peek(), is_digit):
        source.advance()

    return TokenMatch.found(
        Token.make(source, TokenType.NUMBER, float(source.lexeme()))
    )


def token_finder_keyword_or_identifier(c: str, source: Source) -> TokenMatch:
    def is_alpha(char: str) -> bool:
        return char in ascii_letters or char == "_"

    def is_alphanum(char: str) -> bool:
        return is_alpha(char) or char.isdigit()

    if not is_alpha(c):
        return TokenMatch.none()
    while opt_map_or_false(source.peek(), lambda x: is_alphanum(x)):
        source.advance()
    if (keyword := RESERVED_KEYWORDS.get(source.lexeme(), None)) is not None:
        return TokenMatch.found(Token.make(source, keyword))
    else:
        return TokenMatch.found(Token.make(source, TokenType.IDENTIFIER))


TokenFinder = Callable[[str, Source], TokenMatch]


TOKEN_FINDERS: Iterable[TokenFinder] = (
    token_finder_single_char_factory("(", TokenType.LEFT_PAREN),
    token_finder_single_char_factory(")", TokenType.RIGHT_PAREN),
    token_finder_single_char_factory("{", TokenType.LEFT_BRACE),
    token_finder_single_char_factory("}", TokenType.RIGHT_BRACE),
    token_finder_single_char_factory(",", TokenType.COMMA),
    token_finder_single_char_factory(".", TokenType.DOT),
    token_finder_single_char_factory("-", TokenType.MINUS),
    token_finder_single_char_factory("+", TokenType.PLUS),
    token_finder_single_char_factory(";", TokenType.SEMICOLON),
    token_finder_single_char_factory("*", TokenType.STAR),
    token_finder_disambiguate_factory(
        "=", "=", TokenType.EQUAL, TokenType.EQUAL_EQUAL
    ),
    token_finder_disambiguate_factory(
        "!", "=", TokenType.BANG, TokenType.BANG_EQUAL
    ),
    token_finder_disambiguate_factory(
        ">", "=", TokenType.GREATER, TokenType.GREATER_EQUAL
    ),
    token_finder_disambiguate_factory(
        "<", "=", TokenType.LESS, TokenType.LESS_EQUAL
    ),
    token_finder_slash_or_comment,
    token_finder_discard_factory(" ", "\r", "\t"),
    token_finder_newline,
    token_finder_string,
    token_finder_number,
    token_finder_keyword_or_identifier,
)


class Scanner:
    def __init__(
        self,
        source: Source,
        token_finders: Iterable[TokenFinder],
    ):
        self._source = source
        self._token_finders = token_finders

    def scan_tokens(self) -> Iterator[Optional[Token]]:
        """Scan the source code and return an iterable of tokens (or None if the
        current lexeme does not match any token"""
        while not self._source.is_at_end():
            self._source.start_lexeme()
            yield self._scan_token()

        yield Token(TokenType.EOF, "", None, self._source.line())

    def _scan_token(self) -> Optional[Token]:
        """Produce a Token, or None if there is no match.
        Also update errors if detected"""

        c = self._source.advance()

        for finder in self._token_finders:
            token_match = finder(c, self._source)
            match token_match.result:
                case Token() | None:
                    return token_match.result
                case ErrorData():
                    report(asdict(token_match.result))
                    raise ScannerError(token_match.result.message)
                case NotFound():
                    continue
        report(
            asdict(
                ErrorData(
                    self._source.line(), None, f"Invalid character parsed: {c}"
                )
            )
        )
        raise ScannerError("Invalid character.")
