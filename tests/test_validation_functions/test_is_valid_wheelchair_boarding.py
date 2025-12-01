import pytest
from validation_functions.validation_utils import is_valid_wheelchair_boarding

def test_is_valid_wheelchair_boarding_valid_strings():
    assert is_valid_wheelchair_boarding("0") is True
    assert is_valid_wheelchair_boarding("1") is True
    assert is_valid_wheelchair_boarding("2") is True

def test_is_valid_wheelchair_boarding_invalid_strings():
    assert is_valid_wheelchair_boarding("-1") is False
    assert is_valid_wheelchair_boarding("3") is False
    assert is_valid_wheelchair_boarding("") is False
    assert is_valid_wheelchair_boarding(" ") is False
    assert is_valid_wheelchair_boarding("abc") is False
    assert is_valid_wheelchair_boarding("-") is False
    assert is_valid_wheelchair_boarding("1.5") is False

def test_is_valid_wheelchair_boarding_invalid_types():
    assert is_valid_wheelchair_boarding(None) is False
    assert is_valid_wheelchair_boarding(2) is False
    assert is_valid_wheelchair_boarding(1.0) is False
    assert is_valid_wheelchair_boarding(True) is False
    assert is_valid_wheelchair_boarding(["1"]) is False
    assert is_valid_wheelchair_boarding({"1"}) is False
    assert is_valid_wheelchair_boarding((1,)) is False