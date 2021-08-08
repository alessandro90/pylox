from __future__ import annotations  # NOTE: No need since python 3.10+
from exceptions import InternalPyloxError
from typing import Any, Callable, Iterable, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass
from utils.error_handler import ErrorData, ErrorInfo
from utils.functional import try_invoke


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()


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


class Source:
    """Helper class to manage a source file (or repl command)"""

    def __init__(self, source: str):
        self._source = source
        self._source_len = len(self._source)
        self._start = 0
        self._current = 0
        self._line = 1

    def lexeme(self) -> str:
        """Returns the current lexeme"""
        return self._source[self._start : self._current]

    def start_lexeme(self) -> None:
        """Start a new lexeme analysis"""
        self._start = self._current

    def newline(self) -> None:
        """Move to next line"""
        self._line += 1

    def is_at_end(self) -> bool:
        """Returns True if the source has been consumed"""
        return self._current >= self._source_len

    def advance(self) -> str:
        """Consume a character"""
        c = self._source[self._current]
        self._current += 1
        return c

    def peek(self, depth: int = 0) -> Optional[str]:
        """Returns next + detph character, if any, otherwise return None"""
        if self._current + depth >= self._source_len:
            return None
        return self._source[self._current + depth]

    def consume_next_if_is(self, expected: str) -> bool:
        """Returns True if next character matches expected, False otherwise.
        If match is found, consume the character"""

        if self.is_at_end():
            return False
        if self.peek() != expected:
            return False
        self.advance()
        return True

    def line(self) -> int:
        """Returns the current line"""
        return self._line


@dataclass(frozen=True)
class Token:
    """Encapsulates all the relevant information for a Token"""

    token_type: TokenType
    lexeme: str
    literal: Any
    line: int

    @classmethod
    def make(
        cls,
        source: Source,
        token_type: TokenType,
        literal: Any = None,
    ) -> Token:
        return cls(
            token_type=token_type,
            lexeme=source.lexeme(),
            literal=literal,
            line=source.line(),
        )


sentinel_token_not_found = object()  # Sentinel object
TokenFinderResult = Optional[Union[Token, ErrorData, object]]


@dataclass(frozen=True, eq=False)
class TokenMatch:
    """Wrapper to a result from a token_finder_* method"""

    result: TokenFinderResult

    @classmethod
    def none(cls) -> TokenMatch:
        return cls(result=sentinel_token_not_found)

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


def token_finder_disambiguate_two_chars_factory(
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


def token_finder_comment(c: str, source: Source) -> TokenMatch:
    if c != "/":
        return TokenMatch.none()
    if source.consume_next_if_is("/"):
        while try_invoke(source.peek(), lambda x: x != "\n"):
            source.advance()
        return TokenMatch.found()
    else:
        return TokenMatch.found(Token.make(source, TokenType.SLASH))


def token_finder_discard(c: str, source: Source) -> TokenMatch:

    should_discard = lambda x: any((x == " ", x == "\r", x == "\t"))
    if should_discard(c):
        while try_invoke(source.peek(), should_discard):
            source.advance()
        return TokenMatch.found()
    return TokenMatch.none()


def token_finder_newline(c: str, source: Source) -> TokenMatch:
    if c == "\n":
        source.newline()
        return TokenMatch.found()
    return TokenMatch.none()


def token_finder_string(c: str, source: Source) -> TokenMatch:
    if c != '"':
        return TokenMatch.none()

    while try_invoke(char := source.peek(), lambda x: x != '"'):
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

    while try_invoke(source.peek(), is_digit):
        source.advance()

    if try_invoke(source.peek(), lambda char: char == ".") and try_invoke(
        source.peek(1), is_digit
    ):
        source.advance()

    while try_invoke(source.peek(), is_digit):
        source.advance()

    return TokenMatch.found(
        Token.make(source, TokenType.NUMBER, float(source.lexeme()))
    )


def token_finder_keyword_or_identifier(c: str, source: Source) -> TokenMatch:
    if not c.isalnum():
        return TokenMatch.none()
    while try_invoke(source.peek(), lambda x: x.isalnum()):
        source.advance()
    if (keyword := RESERVED_KEYWORDS.get(source.lexeme(), None)) is not None:
        return TokenMatch.found(Token.make(source, keyword))
    else:
        return TokenMatch.found(Token.make(source, TokenType.IDENTIFIER))


TOKEN_FINDERS = (
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
    token_finder_disambiguate_two_chars_factory(
        "=", "=", TokenType.EQUAL, TokenType.EQUAL_EQUAL
    ),
    token_finder_disambiguate_two_chars_factory(
        "!", "=", TokenType.BANG, TokenType.BANG_EQUAL
    ),
    token_finder_disambiguate_two_chars_factory(
        ">", "=", TokenType.GREATER, TokenType.GREATER_EQUAL
    ),
    token_finder_disambiguate_two_chars_factory(
        "<", "=", TokenType.LESS, TokenType.LESS_EQUAL
    ),
    token_finder_comment,
    token_finder_discard,
    token_finder_newline,
    token_finder_string,
    token_finder_number,
    token_finder_keyword_or_identifier,
)


class Scanner:
    def __init__(
        self,
        source: Source,
        token_finders: Iterable[Callable[[str, Source], TokenMatch]],
    ):
        self._source = source
        self._token_finders = token_finders
        self._error = ErrorInfo()

    def error_info(self) -> Optional[ErrorInfo]:
        """Return error information, if any"""
        if self._error.has_error():
            return self._error
        else:
            return None

    def scan_tokens(self) -> Iterable[Optional[Token]]:
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
            if token_match.result is sentinel_token_not_found:
                continue
            elif token_match.result is None or isinstance(
                token_match.result, Token
            ):
                return token_match.result
            elif isinstance(token_match.result, ErrorData):
                self._error.push(token_match.result)
                return None
        raise InternalPyloxError(
            "Unexpected internal error. "
            f"class: {self.__class__.__name__}, file: {__file__}"
        )
