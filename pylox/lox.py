from scanner import Scanner
from utils.file_reader import read_as_string

EXIT_COMMAND = "exit()"


class PyLox:
    def __init__(self) -> None:
        self._scanner = Scanner()

    def run_file(self, script: str) -> None:
        self._run(read_as_string(script))

    def run_prompt(self) -> None:
        try:
            while (command := input("> ")) != EXIT_COMMAND:
                self._run(command)
        except EOFError:
            pass

    def _run(self, string: str) -> None:
        pass
