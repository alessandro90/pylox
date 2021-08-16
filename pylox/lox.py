from scanner import Scanner, TOKEN_FINDERS
from source import Source
from utils.file_reader import read_as_string
from utils.error_handler import ErrorInfo
from typing import Optional
import sys
from pyloxparser import Parser
from visitors import Stringyfier

_EXIT_COMMAND = "exit()"


def run_file(script: str) -> None:
    if (err := _run(read_as_string(script))) is not None:
        err.display()
        sys.exit(65)


def run_prompt() -> None:
    try:
        while (command := input("> ")) != _EXIT_COMMAND:
            if (err := _run(command)) is not None:
                err.display()
    except (EOFError, KeyboardInterrupt):
        pass


def _run(source: str) -> Optional[ErrorInfo]:
    scanner = Scanner(Source(source), TOKEN_FINDERS)
    tokens = scanner.scan_tokens()

    ast = Parser(tokens)
    result = ast.parse()
    s = Stringyfier()
    print(s.stringify(result))
    # for (i, t) in enumerate(tokens):
    #     print(f"{i} => {t}")
    return scanner.error_info()
