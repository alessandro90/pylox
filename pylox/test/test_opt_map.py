from utils.functional import opt_map, opt_map_or_false


def test_opt_map_on_value():
    val = 15
    assert opt_map(val, lambda x: isinstance(x, str), True) is False


def test_opt_map_on_None():
    assert opt_map(None, lambda x: x.isdigit(), False) is False


def test_opt_map_false_with_value():
    val = 10
    assert opt_map_or_false(val, lambda x: x % 2 == 0) is True


def test_opt_map_false_with_None():
    assert opt_map_or_false(None, lambda x: x % 2 == 0) is False
