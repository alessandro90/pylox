from exceptions import ScannerError
import pyloxscanner as s
from source import Source
from pyloxtoken import Token, TokenType
import pytest
from error_handler import ErrorData


@pytest.fixture
def a_source():
    return Source("Dummy source text")


def test_token_finder_single_char_not_found(a_source):
    find_dot = s.token_finder_single_char_factory(".", TokenType.DOT)
    assert find_dot("-", a_source).result == s.TokenMatch.none().result


def test_token_finder_single_char_found(a_source):
    find_dot = s.token_finder_single_char_factory(".", TokenType.DOT)
    assert find_dot(".", a_source).result == Token.make(a_source, TokenType.DOT)


def test_token_finder_disambiguate_not_found(a_source):
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", TokenType.EQUAL, TokenType.EQUAL_EQUAL
    )

    assert (
        find_eq_or_double_eq(".", a_source).result == s.TokenMatch.none().result
    )


def test_token_finder_disambiguate_found_first():
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", TokenType.EQUAL, TokenType.EQUAL_EQUAL
    )

    source = Source(";")

    assert find_eq_or_double_eq("=", source).result == Token.make(
        source, TokenType.EQUAL
    )


def test_token_finder_disambiguate_found_second():
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", TokenType.EQUAL, TokenType.EQUAL_EQUAL
    )

    source = Source("=")

    assert find_eq_or_double_eq("=", source).result == Token.make(
        source, TokenType.EQUAL_EQUAL
    )


def test_token_finder_slash_or_comment_not_found(a_source):
    assert (
        s.token_finder_slash_or_comment(".", a_source).result
        == s.TokenMatch.none().result
    )


def test_token_finder_slash_or_comment_found_single_line():
    source = Source("/ this is a single line comment")
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.is_at_end()


def test_token_finder_slash_or_comment_found_single_line_with_newline():
    source = Source("/ this is a single line comment\n")
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.is_at_end() is False


def test_token_finder_slash_or_comment_found_multi_line():
    text = "* this is a multi line comment\nSpanning exactly\n3 lines*/"
    source = Source(text)
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.line() == len(text.splitlines())


def test_token_finder_slash_or_comment_found_multi_line_untermined():
    text = "* this is a multi line comment\nSpanning exactly\n3 lines"
    source = Source(text)
    assert s.token_finder_slash_or_comment("/", source).result == ErrorData(
        source.line(), None, "Untermined comment"
    )
    assert source.is_at_end()


def test_token_finder_discard_not_found(a_source):
    assert (
        s.token_finder_discard_factory("x", "y", "z")("a", a_source).result
        == s.TokenMatch.none().result
    )


def test_token_finder_discard_found():
    discard = s.token_finder_discard_factory("a", "b", "c")
    source_text = "abcabaaFccc"
    source = Source(source_text)
    assert discard("b", source).result is None
    assert source.lexeme() == "abcabaa"


def test_token_finder_newline_not_found(a_source):
    assert (
        s.token_finder_newline("x", a_source).result
        == s.TokenMatch.none().result
    )


def test_token_finder_newline_found(a_source):
    assert s.token_finder_newline("\n", a_source).result is None
    assert a_source.line() == 2


def test_token_finder_string_not_found(a_source):
    assert (
        s.token_finder_string("x", a_source).result
        == s.TokenMatch.none().result
    )


def test_token_finder_string_found():
    source = Source('"string"')
    c = source.advance()
    assert s.token_finder_string(c, source).result == Token.make(
        source, TokenType.STRING, "string"
    )


def test_token_finder_multiline_string_found():
    source = Source('"multiline\nstring"')
    c = source.advance()
    assert s.token_finder_string(c, source).result == Token.make(
        source, TokenType.STRING, "multiline\nstring"
    )
    assert source.line() == 2


def test_token_finder_multiline_untermined_string_found():
    source = Source('"multiline\nstring')
    c = source.advance()
    assert s.token_finder_string(c, source).result == ErrorData(
        source.line(), None, "Untermined string"
    )
    assert source.line() == 2


def test_token_finder_find_number_not_found(a_source):
    assert (
        s.token_finder_number("a", a_source).result
        == s.TokenMatch.none().result
    )
    assert (
        s.token_finder_number(".", a_source).result
        == s.TokenMatch.none().result
    )


def test_token_finder_find_number_integer_found():
    source = Source("12569")
    c = source.advance()
    assert s.token_finder_number(c, source).result == Token.make(
        source, TokenType.NUMBER, 12569
    )


def test_token_finder_find_number_decimal_found():
    source = Source("12569.778")
    c = source.advance()
    assert s.token_finder_number(c, source).result == Token.make(
        source, TokenType.NUMBER, 12569.778
    )


def test_token_finder_keyword_or_identifier_not_found(a_source):
    chars = ".,;-+*/{}()[]\n<>\t =!"

    for c in chars:
        assert (
            s.token_finder_keyword_or_identifier(c, a_source).result
            == s.TokenMatch.none().result
        )


def test_token_finder_keyword_or_identifier_keyword_found():
    for (string, token_type) in s.RESERVED_KEYWORDS.items():
        source = Source(string)
        c = source.advance()
        assert s.token_finder_keyword_or_identifier(
            c, source
        ).result == Token.make(source, token_type)


def test_token_finder_keyword_or_identifier_identifier_found():
    words = [
        "apple",
        "banana",
        "people",
        "wowoww",
        "class_",
        "_if_",
        "vAr",
        "my_var_4",
        "_",
    ]
    for word in words:
        source = Source(word)
        c = source.advance()
        assert s.token_finder_keyword_or_identifier(
            c, source
        ).result == Token.make(source, TokenType.IDENTIFIER)


def test_scanner_regular_source():
    source = Source(". class () {;fun")
    scanner = s.Scanner(source, s.TOKEN_FINDERS)
    tokens = list(scanner.scan_tokens())
    assert tokens[0] is not None and tokens[0].token_type == TokenType.DOT
    assert tokens[1] is None
    assert tokens[2] is not None and tokens[2].token_type is TokenType.CLASS
    assert tokens[3] is None
    assert (
        tokens[4] is not None and tokens[4].token_type is TokenType.LEFT_PAREN
    )
    assert (
        tokens[5] is not None and tokens[5].token_type is TokenType.RIGHT_PAREN
    )
    assert tokens[6] is None
    assert (
        tokens[7] is not None and tokens[7].token_type is TokenType.LEFT_BRACE
    )
    assert tokens[8] is not None and tokens[8].token_type is TokenType.SEMICOLON
    assert tokens[9] is not None and tokens[9].token_type is TokenType.FUN


def test_scanner_with_invalid_char():
    source = Source(". 'class () {;fun")
    scanner = s.Scanner(source, s.TOKEN_FINDERS)
    tokens = scanner.scan_tokens()
    next(tokens)
    next(tokens)
    try:
        next(tokens)
    except ScannerError:
        assert True
    else:
        assert False
