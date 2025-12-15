import pytest
from validation_functions.validation_utils import is_valid_continuous_drop_off

def test_is_valid_continuous_drop_off_valid_values():
    assert is_valid_continuous_drop_off(0) is True
    assert is_valid_continuous_drop_off(1) is True
    assert is_valid_continuous_drop_off(2) is True
    assert is_valid_continuous_drop_off(3) is True

def test_is_valid_continuous_drop_off_invalid_values():
    assert is_valid_continuous_drop_off(-1) is False
    assert is_valid_continuous_drop_off(4) is False

def test_is_valid_continuous_drop_off_invalid_types():
    assert is_valid_continuous_drop_off(None) is False
    assert is_valid_continuous_drop_off("0") is False
    assert is_valid_continuous_drop_off(1.0) is False
    assert is_valid_continuous_drop_off(True) is False
    assert is_valid_continuous_drop_off(["1"]) is False
    assert is_valid_continuous_drop_off({"1"}) is False
    assert is_valid_continuous_drop_off((1,)) is False