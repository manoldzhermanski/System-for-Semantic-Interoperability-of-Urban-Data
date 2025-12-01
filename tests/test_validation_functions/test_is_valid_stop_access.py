import pytest
from validation_functions.validation_utils import is_valid_stop_access

def test_is_valid_stop_access_valid_strings():
    assert is_valid_stop_access("0") is True
    assert is_valid_stop_access("1") is True

def test_is_valid_stop_access_invalid_strings():
    assert is_valid_stop_access("-1") is False
    assert is_valid_stop_access("2") is False
    assert is_valid_stop_access("") is False
    assert is_valid_stop_access(" ") is False
    assert is_valid_stop_access("abc") is False
    assert is_valid_stop_access("-") is False
    assert is_valid_stop_access("1.5") is False

def test_is_valid_stop_access_invalid_types():
    assert is_valid_stop_access(None) is False
    assert is_valid_stop_access(2) is False
    assert is_valid_stop_access(1.0) is False
    assert is_valid_stop_access(True) is False
    assert is_valid_stop_access(["1"]) is False
    assert is_valid_stop_access({"1"}) is False
    assert is_valid_stop_access((1,)) is False