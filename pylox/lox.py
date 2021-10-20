from scanner import Scanner, TOKEN_FINDERS
from source import Source
from utils.file_reader import read_as_string
import sys
from pyloxparser import Parser
from pyloxinterpreter import Interpreter
from pyloxresolver import Resolver

# from visitors import Stringyfier

_EXIT_COMMAND = ["exit!", "quit!"]


class Lox:
    def __init__(self):
        self._interpreter = Interpreter()

    def run_file(self, script: str) -> None:
        if (exit_code := self._run(read_as_string(script))) != 0:
            sys.exit(exit_code)

    def run_prompt(self) -> None:
        self._interpreter.set_repl()
        try:
            while (command := input("> ")) not in _EXIT_COMMAND:
                self._run(command)
        except (EOFError, KeyboardInterrupt):
            pass

    def _run(self, source: str) -> int:
        tokens = Scanner(Source(source), TOKEN_FINDERS).scan_tokens()
        statements = Parser(tokens).parse()
        if statements is None:
            return 65
        if len(statements) == 0:
            return 0
        if not Resolver(self._interpreter).resolve_statements(statements):
            return 65
        if not self._interpreter.interpret(statements):
            return 70
        return 0
