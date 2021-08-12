import pytest
from source import Source
from string import ascii_letters, digits


@pytest.fixture
def example_text():
    return """Some text
to be used as a
test for the source methods"""


def test_source_initialization(example_text):
    source = Source(example_text)

    assert source.line() == 1  # Line 1 at start
    assert source.lexeme() == ""
    assert source.is_at_end() is False
    assert source.peek() == example_text[0]


def test_source_newline(example_text):
    source = Source(example_text)

    source.newline()
    assert source.line() == 2


def test_source_advance(example_text):
    source = Source(example_text)

    counter = 0
    while not source.is_at_end():
        c = source.advance()
        assert c == example_text[counter]
        counter += 1
        if counter < len(example_text):
            assert source.peek() == example_text[counter]

    assert source.is_at_end()
    assert source.peek() is None


def test_source_consume_next_if_is(example_text):
    source = Source(example_text)

    not_in_text = [
        char for char in ascii_letters + digits if char not in example_text
    ]

    counter = 0
    while not source.is_at_end():
        assert all(not source.consume_next_if_is(cx) for cx in not_in_text)
        assert source.consume_next_if_is(example_text[counter])
        counter += 1

    assert all(not source.consume_next_if_is(char) for char in example_text)
