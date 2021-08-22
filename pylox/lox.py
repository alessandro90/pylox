from scanner import Scanner, TOKEN_FINDERS
from source import Source
from utils.file_reader import read_as_string
import sys
from pyloxparser import Parser
from visitors import Stringyfier

_EXIT_COMMAND = "exit()"


def run_file(script: str) -> None:
    if not _run(read_as_string(script)):
        sys.exit(65)


def run_prompt() -> None:
    try:
        while (command := input("> ")) != _EXIT_COMMAND:
            _run(command)
    except (EOFError, KeyboardInterrupt):
        pass


def _run(source: str) -> bool:
    tokens = Scanner(Source(source), TOKEN_FINDERS).scan_tokens()
    result = Parser(tokens).parse()
    if result is None:
        return False
    else:
        s = Stringyfier()
        print(s.stringify(result))
        # for (i, t) in enumerate(tokens):
        #     print(f"{i} => {t}")
        return True
