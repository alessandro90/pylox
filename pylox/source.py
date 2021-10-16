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
        if self.is_at_end():
            return ""
        c = self._source[self._current]
        self._current += 1
        return c

    def peek(self, depth: int = 0) -> str | None:
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
