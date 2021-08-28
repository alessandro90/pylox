from pyloxtoken import Token


class InternalPyloxError(Exception):
    pass


class ParserError(Exception):
    pass


class ScannerError(Exception):
    pass


class PyloxRuntimeError(Exception):
    def __init__(self, token: Token, msg: str):
        super().__init__(msg)
        self.token = token


class PyloxDivisionByZeroError(PyloxRuntimeError):
    pass
