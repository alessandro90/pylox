import scanner as s
import pytest
from utils.error_handler import ErrorData


@pytest.fixture
def a_source():
    return s.Source("Dummy source text")


def test_token_finder_single_char_not_found(a_source):
    find_dot = s.token_finder_single_char_factory(".", s.TokenType.DOT)
    assert find_dot("-", a_source).result is s.SENTINEL_TOKEN_NOT_FOUND


def test_token_finder_single_char_found(a_source):
    find_dot = s.token_finder_single_char_factory(".", s.TokenType.DOT)
    assert find_dot(".", a_source).result == s.Token.make(
        a_source, s.TokenType.DOT
    )


def test_token_finder_disambiguate_not_found(a_source):
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", s.TokenType.EQUAL, s.TokenType.EQUAL_EQUAL
    )

    assert (
        find_eq_or_double_eq(".", a_source).result is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_disambiguate_found_first():
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", s.TokenType.EQUAL, s.TokenType.EQUAL_EQUAL
    )

    source = s.Source(";")

    assert find_eq_or_double_eq("=", source).result == s.Token.make(
        source, s.TokenType.EQUAL
    )


def test_token_finder_disambiguate_found_second():
    find_eq_or_double_eq = s.token_finder_disambiguate_factory(
        "=", "=", s.TokenType.EQUAL, s.TokenType.EQUAL_EQUAL
    )

    source = s.Source("=")

    assert find_eq_or_double_eq("=", source).result == s.Token.make(
        source, s.TokenType.EQUAL_EQUAL
    )


def test_token_finder_slash_or_comment_not_found(a_source):
    assert (
        s.token_finder_slash_or_comment(".", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_slash_or_comment_found_single_line():
    source = s.Source("/ this is a single line comment")
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.is_at_end()


def test_token_finder_slash_or_comment_found_single_line_with_newline():
    source = s.Source("/ this is a single line comment\n")
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.is_at_end() is False


def test_token_finder_slash_or_comment_found_multi_line():
    text = "* this is a multi line comment\nSpanning exactly\n3 lines*/"
    source = s.Source(text)
    assert s.token_finder_slash_or_comment("/", source).result is None
    assert source.line() == len(text.splitlines())


def test_token_finder_slash_or_comment_found_multi_line_untermined():
    text = "* this is a multi line comment\nSpanning exactly\n3 lines"
    source = s.Source(text)
    assert s.token_finder_slash_or_comment("/", source).result == ErrorData(
        source.line(), None, "Untermined comment"
    )
    assert source.is_at_end()


def test_token_finder_discard_not_found(a_source):
    assert (
        s.token_finder_discard_factory("x", "y", "z")("a", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_discard_found():
    discard = s.token_finder_discard_factory("a", "b", "c")
    source_text = "abcabaaFccc"
    source = s.Source(source_text)
    assert discard("b", source).result is None
    assert source.lexeme() == "abcabaa"


def test_token_finder_newline_not_found(a_source):
    assert (
        s.token_finder_newline("x", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_newline_found(a_source):
    assert s.token_finder_newline("\n", a_source).result is None
    assert a_source.line() == 2


def test_token_finder_string_not_found(a_source):
    assert (
        s.token_finder_string("x", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_string_found():
    source = s.Source('"string"')
    c = source.advance()
    assert s.token_finder_string(c, source).result == s.Token.make(
        source, s.TokenType.STRING, "string"
    )


def test_token_finder_multiline_string_found():
    source = s.Source('"multiline\nstring"')
    c = source.advance()
    assert s.token_finder_string(c, source).result == s.Token.make(
        source, s.TokenType.STRING, "multiline\nstring"
    )
    assert source.line() == 2


def test_token_finder_multiline_untermined_string_found():
    source = s.Source('"multiline\nstring')
    c = source.advance()
    assert s.token_finder_string(c, source).result == ErrorData(
        source.line(), None, "Untermined string"
    )
    assert source.line() == 2


def test_token_finder_find_number_not_found(a_source):
    assert (
        s.token_finder_number("a", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )
    assert (
        s.token_finder_number(".", a_source).result
        is s.SENTINEL_TOKEN_NOT_FOUND
    )


def test_token_finder_find_number_integer_found():
    source = s.Source("12569")
    c = source.advance()
    assert s.token_finder_number(c, source).result == s.Token.make(
        source, s.TokenType.NUMBER, 12569
    )


def test_token_finder_find_number_decimal_found():
    source = s.Source("12569.778")
    c = source.advance()
    assert s.token_finder_number(c, source).result == s.Token.make(
        source, s.TokenType.NUMBER, 12569.778
    )


def test_token_finder_keyword_or_identifier_not_found(a_source):
    chars = ".,;-+*/{}()[]\n<>\t =!"

    for c in chars:
        assert (
            s.token_finder_keyword_or_identifier(c, a_source).result
            is s.SENTINEL_TOKEN_NOT_FOUND
        )


def test_token_finder_keyword_or_identifier_keyword_found():
    for (string, token_type) in s.RESERVED_KEYWORDS.items():
        source = s.Source(string)
        c = source.advance()
        assert s.token_finder_keyword_or_identifier(
            c, source
        ).result == s.Token.make(source, token_type)


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
        source = s.Source(word)
        c = source.advance()
        assert s.token_finder_keyword_or_identifier(
            c, source
        ).result == s.Token.make(source, s.TokenType.IDENTIFIER)
