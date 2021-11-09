from pyloxscanner import Scanner, TOKEN_FINDERS
from source import Source
import sys
from pyloxparser import Parser
from pyloxinterpreter import Interpreter
from pyloxresolver import Resolver

# from visitors import Stringyfier

_EXIT_COMMAND = ["exit!", "quit!"]


def _read_as_string(fname: str) -> str:
    """Return file content as a single string"""
    with open(fname, mode="r") as source:
        return source.read()


class Lox:
    def __init__(self):
        self._interpreter = Interpreter()

    def run_file(self, script: str) -> None:
        if (exit_code := self._run(_read_as_string(script))) != 0:
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
        if not statements:
            return 0
        if not Resolver(self._interpreter).resolve_statements(statements):
            return 65
        if not self._interpreter.interpret(statements):
            return 70
        return 0
