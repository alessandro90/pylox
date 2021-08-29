from scanner import Scanner, TOKEN_FINDERS
from source import Source
from utils.file_reader import read_as_string
import sys
from pyloxparser import Parser
from typing import Optional
from pyloxinterpreter import Interpreter

# from visitors import Stringyfier

_EXIT_COMMAND = ["exit!", "quit!"]


class Lox:
    def __init__(self):
        self._interpreter = Interpreter()

    def run_file(self, script: str) -> None:
        result = self._run(read_as_string(script))
        if result is not None:
            sys.exit(result)

    def run_prompt(self) -> None:
        try:
            while (command := input("> ")) not in _EXIT_COMMAND:
                self._run(command)
        except (EOFError, KeyboardInterrupt):
            pass

    def _run(self, source: str) -> Optional[int]:
        tokens = Scanner(Source(source), TOKEN_FINDERS).scan_tokens()
        statements = Parser(tokens).parse()
        if statements is None:
            return 65
        if not self._interpreter.interpret(statements):
            return 70
        return None
