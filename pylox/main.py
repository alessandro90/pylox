import sys
from lox import run_file, run_prompt
import logging


def main(args: list[str]) -> None:
    """Run the script or start the repl."""

    logging.basicConfig(level=logging.DEBUG)

    if len(args) == 1:
        logging.debug("run_prompt")
        run_prompt()
    elif len(args) == 2:
        _, script = args
        logging.debug(f"run_file {script}")
        run_file(script)
    else:
        print("Usage: python main.py [script]")
        sys.exit(64)


if __name__ == "__main__":
    main(sys.argv)
