import pytest
from validation_functions.validation_utils import is_valid_is_bidirectional

def test_is_valid_is_bidirectional_valid_values():
    assert is_valid_is_bidirectional(0) is True
    assert is_valid_is_bidirectional(1) is True

def test_is_valid_is_bidirectional_invalid_values():
    assert is_valid_is_bidirectional(-1) is False
    assert is_valid_is_bidirectional(2) is False

def test_is_valid_is_bidirectional_invalid_types():
    assert is_valid_is_bidirectional(None) is False
    assert is_valid_is_bidirectional("0") is False
    assert is_valid_is_bidirectional(1.0) is False
    assert is_valid_is_bidirectional(True) is False
    assert is_valid_is_bidirectional(["1"]) is False
    assert is_valid_is_bidirectional({"1"}) is False
    assert is_valid_is_bidirectional((1,)) is False