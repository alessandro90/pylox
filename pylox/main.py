import sys
from lox import PyLox
import logging


def main(args: list[str]) -> None:
    """Run the script or start the repl."""

    logging.basicConfig(level=logging.DEBUG)

    pylox = PyLox()
    if len(args) == 1:
        logging.debug("run_prompt")
        pylox.run_prompt()
    elif len(args) == 2:
        logging.debug(f"run_file {args[1]}")
        pylox.run_file(args[1])
    else:
        print("Usage: python main.py [script]")
        sys.exit(64)


if __name__ == "__main__":
    main(sys.argv)
