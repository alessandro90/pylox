from __future__ import annotations  # TODO: No need since python 3.10+
from typing import Any, Callable, Iterable, Optional, TypeVar
from enum import Enum, auto
from dataclasses import dataclass
from utils.error_handler import ErrorData, ErrorInfo

# Generics types
T = TypeVar("T")
Q = TypeVar("Q")


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
        """Returns next character, if any"""
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


class Scanner:
    def __init__(self, source: Source):
        self._source = source
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

    def _recursion_if_not_eof(self) -> Optional[Token]:
        """Return the result of _scan_token if source is not finished,
        None otherwise"""
        if not self._source.is_at_end():
            return self._scan_token()
        return None

    def _scan_token(self) -> Optional[Token]:
        """Produce a Token, or None if there is no match.
        Also update errors if detected"""
        c = self._source.advance()
        if c == "(":
            return Token.make(self._source, TokenType.LEFT_PAREN)
        if c == ")":
            return Token.make(self._source, TokenType.RIGHT_PAREN)
        if c == "{":
            return Token.make(self._source, TokenType.LEFT_BRACE)
        if c == "}":
            return Token.make(self._source, TokenType.RIGHT_BRACE)
        if c == ",":
            return Token.make(self._source, TokenType.COMMA)
        if c == ".":
            return Token.make(self._source, TokenType.DOT)
        if c == "-":
            return Token.make(self._source, TokenType.MINUS)
        if c == "+":
            return Token.make(self._source, TokenType.PLUS)
        if c == ";":
            return Token.make(self._source, TokenType.SEMICOLON)
        if c == "*":
            return Token.make(self._source, TokenType.STAR)
        if c == "!":
            if self._source.consume_next_if_is("="):
                return Token.make(self._source, TokenType.BANG_EQUAL)
            else:
                return Token.make(self._source, TokenType.BANG)
        if c == "=":
            if self._source.consume_next_if_is("="):
                return Token.make(self._source, TokenType.EQUAL_EQUAL)
            else:
                return Token.make(self._source, TokenType.EQUAL)
        if c == "<":
            if self._source.consume_next_if_is("="):
                return Token.make(self._source, TokenType.LESS_EQUAL)
            else:
                return Token.make(self._source, TokenType.LESS)
        if c == ">":
            if self._source.consume_next_if_is("="):
                return Token.make(self._source, TokenType.GREATER_EQUAL)
            else:
                return Token.make(self._source, TokenType.GREATER)
        if c == "/":
            if self._source.consume_next_if_is("/"):
                while try_invoke(self._source.peek(), lambda x: x != "\n"):
                    self._source.advance()
                return self._recursion_if_not_eof()
            else:
                return Token.make(self._source, TokenType.SLASH)
        if any((c == " ", c == "\r", c == "\t")):
            return self._recursion_if_not_eof()
        if c == "\n":
            self._source.newline()
            return None
        if c == '"':
            while try_invoke(char := self._source.peek(), lambda x: x != ""):
                if char == "\n":
                    self._source.newline()
                self._source.advance()
            if self._source.is_at_end():
                self._error.push(
                    ErrorData(self._source.line(), None, "Untermined string")
                )
                return None
            else:
                self._source.advance()
                return Token.make(
                    self._source, TokenType.STRING, self._source.lexeme()[1:-1]
                )
        if c.isdigit():

            is_digit = lambda char: char.isdigit()  # noqa E731

            while try_invoke(self._source.peek(), is_digit):
                self._source.advance()

            if try_invoke(
                self._source.peek(), lambda char: char == "."
            ) and try_invoke(self._source.peek(1), is_digit):
                self._source.advance()

            while try_invoke(self._source.peek(), is_digit):
                self._source.advance()

            return Token.make(
                self._source, TokenType.NUMBER, float(self._source.lexeme())
            )

        self._error.push(
            ErrorData(self._source.line(), None, f"Unexpected character: {c}")
        )
        return None


def try_invoke(
    val: Optional[T], callable: Callable[[T], Q], default: Optional[Q] = None
) -> Optional[Q]:
    """Return callable(var) if var is not None, otherwise return default"""
    if val is None:
        return default
    return callable(val)
