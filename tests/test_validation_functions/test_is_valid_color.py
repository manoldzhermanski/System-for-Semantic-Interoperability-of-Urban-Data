import pytest
from validation_functions.validation_utils import is_valid_color

def test_is_valid_color_valid_strings():
    assert is_valid_color("FFFFFF") is True
    assert is_valid_color("000000") is True
    assert is_valid_color("a1b2c3") is True
    assert is_valid_color("A1B2C3") is True
    assert is_valid_color("  AABBCC  ") is True

def test_is_valid_color_invalid_strings():
    assert is_valid_color("") is False
    assert is_valid_color("   ") is False
    assert is_valid_color("FFF") is False
    assert is_valid_color("FFFFFFF") is False
    assert is_valid_color("GHIJKL") is False
    assert is_valid_color("12345G") is False
    assert is_valid_color("12 345") is False
    assert is_valid_color("#FFFFFF") is False

    
def test_is_valid_color_invalid_types():
    assert is_valid_color(None) is False
    assert is_valid_color(123) is False
    assert is_valid_color(3.14) is False
    assert is_valid_color([]) is False
    assert is_valid_color({}) is False
    assert is_valid_color(()) is False
    assert is_valid_color(True) is False