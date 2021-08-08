from utils.functional import try_invoke, try_invoke_bool


def test_try_invoke_on_value():
    val = 15
    assert try_invoke(val, lambda x: isinstance(x, str), True) is False


def test_try_invoke_on_None():
    assert try_invoke(None, lambda x: x.isdigit(), False) is False


def test_try_invoke_bool_with_value():
    val = 10
    assert try_invoke_bool(val, lambda x: x % 2 == 0) is True


def test_try_invoke_bool_with_None():
    assert try_invoke_bool(None, lambda x: x % 2 == 0) is False
