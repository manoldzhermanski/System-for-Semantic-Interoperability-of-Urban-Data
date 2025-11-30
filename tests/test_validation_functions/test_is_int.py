import pytest
from validation_functions.validation_utils import is_int

def test_valid_integers():
    assert is_int("0") is True
    assert is_int("10") is True
    assert is_int("-5") is True
    assert is_int("+12") is True
    assert is_int("   7   ") is True

def test_invalid_strings():
    assert is_int("3.14") is False
    assert is_int("abc") is False
    assert is_int("12abc") is False
    assert is_int("--5") is False
    assert is_int("-") is False
    assert is_int("1 2") is False

def test_edge_cases():
    assert is_int("") is False
    assert is_int(" ") is False
    assert is_int("\t\n") is False

def test_invalid_types():
    assert is_int(None) is False
    assert is_int(123) is False
    assert is_int(3.14) is False
    assert is_int(True) is False
    assert is_int(["1"]) is False
    assert is_int({"value": "1"}) is False
    assert is_int((1)) is False
    