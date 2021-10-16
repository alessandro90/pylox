from __future__ import annotations  # NOTE: No need since python 3.11+
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any
from source import Source


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
