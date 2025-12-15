import pytest
from validation_functions.validation_utils import is_valid_bikes_allowed

def test_is_valid_bikes_allowed_valid_values():
    assert is_valid_bikes_allowed(0) is True
    assert is_valid_bikes_allowed(1) is True
    assert is_valid_bikes_allowed(2) is True

def test_is_valid_bikes_allowed_invalid_values():
    assert is_valid_bikes_allowed(-1) is False
    assert is_valid_bikes_allowed(3) is False

def test_is_valid_bikes_allowed_invalid_types():
    assert is_valid_bikes_allowed(None) is False
    assert is_valid_bikes_allowed("0") is False
    assert is_valid_bikes_allowed(1.0) is False
    assert is_valid_bikes_allowed(True) is False
    assert is_valid_bikes_allowed(["1"]) is False
    assert is_valid_bikes_allowed({"1"}) is False
    assert is_valid_bikes_allowed((1,)) is False