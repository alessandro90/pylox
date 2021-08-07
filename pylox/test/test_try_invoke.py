from utils.functional import try_invoke


def test_try_invoke_on_value():
    val = "10"
    assert try_invoke(val, lambda x: x.isdigit())


def test_try_invoke_on_none():
    assert try_invoke(None, lambda _: True) is None


def test_try_invoke_on_value_with_default():
    val = 15
    assert not try_invoke(val, lambda x: isinstance(x, str), True)


def test_try_invoke_on_None_with_default():
    assert not try_invoke(None, lambda x: x.isdigit(), False)
