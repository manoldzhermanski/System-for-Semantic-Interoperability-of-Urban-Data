import pytest
from gtfs_static.gtfs_static_utils import parse_float


def test_parse_float_none_value_as_input():
    """
    Check that if a None value is given as input, None value is returned
    
    """
    assert parse_float(None, "test_field") is None


def test_parse_float_empty_string_as_input():
    """
    Check that if an empty string is given as input, None value is returned
    """
    assert parse_float("", "test_field") is None


def test_parse_float_whitespace_string_as_input():
    """
    Check that if a white spaces are given as input, None value is returned
    """
    assert parse_float("   ", "test_field") is None


def test_parse_float_valid_float():
    """
    Check that if a valid float string representation is given as input, it's converted to float
    """
    assert parse_float("3.14", "test_field") == 3.14


def test_parse_float_valid_float_with_spaces():
    """
    Check that if a valid float representation surrounded by white spaces is given as input,
    the white spaces are trimmed anf it's converted to float
    """
    assert parse_float("  2.5  ", "test_field") == 2.5


def test_parse_float_integer_string_as_input():
    """
    Check that if an integer is given as input, it's converted to float
    """
    assert parse_float("10", "test_field") == 10.0


def test_parse_float_invalid_value_raises_value_error():
    """
    Check that an invalid value raises ValueError
    """
    with pytest.raises(ValueError) as exc:
        parse_float("abc", "price")

    assert str(exc.value) == "price must be float, got 'abc'"
