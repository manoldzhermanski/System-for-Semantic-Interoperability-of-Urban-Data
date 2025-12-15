import pytest
from gtfs_static.gtfs_static_utils import parse_int

def test_parse_int_none_value_as_input():
    """
    Check that if a None value is given as input, None value is returned
    """
    assert parse_int(None, "test_field") is None


def test_parse_int_empty_string_as_input():
    """
    Check that if an empty string is given as input, None value is returned
    """
    assert parse_int("", "test_field") is None


def test_parse_int_whitespace_string_as_input():
    """
    Check thst if a white spaces are given as input, None value is returned
    """
    assert parse_int("   ", "test_field") is None


def test_parse_int_valid_integer():
    """
    Check that if a valid integer string representation is given as input, it's converted to int
    """
    assert parse_int("42", "test_field") == 42


def test_parse_int_valid_integer_with_spaces():
    """
    Check that if a valid integer representation surrounded by white spaces is given as input,
    the white spaces are trimmed anf it's converted to int
    """
    assert parse_int("  7  ", "test_field") == 7


def test_parse_int_invalid_integer_raises_value_error():
    """
    Check that an invalid value raises ValueError
    """
    with pytest.raises(ValueError) as exc:
        parse_int("abc", "age")

    assert str(exc.value) == "age must be integer, got 'abc'"
