import pytest
from validation_functions.validation_utils import is_float

def test_valid_integers():
    assert is_float("0.0") is True
    assert is_float("10") is True
    assert is_float("-3.14") is True
    assert is_float("5.") is True
    assert is_float(".5") is True
    assert is_float("   2.0   ") is True

def test_invalid_floats():
    assert is_float("") is False
    assert is_float(" ") is False
    assert is_float("\t\n") is False
    assert is_float("-") is False
    assert is_float("3,14") is False
    assert is_float("abc") is False
    assert is_float("12abc") is False
    assert is_float("2.13.15") is False
    assert is_float("..5") is False
    assert is_float("5..") is False

def test_invalid_types():
    assert is_float(None) is False
    assert is_float(123) is False
    assert is_float(3.14) is False
    assert is_float(True) is False
    assert is_float(["1"]) is False
    assert is_float({"value": "1"}) is False
    assert is_float((1)) is False