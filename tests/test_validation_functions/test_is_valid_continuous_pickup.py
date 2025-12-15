import pytest
from validation_functions.validation_utils import is_valid_continuous_pickup

def test_is_valid_continuous_pickup_valid_values():
    assert is_valid_continuous_pickup(0) is True
    assert is_valid_continuous_pickup(1) is True
    assert is_valid_continuous_pickup(2) is True
    assert is_valid_continuous_pickup(3) is True

def test_is_valid_continuous_pickup_invalid_values():
    assert is_valid_continuous_pickup(-1) is False
    assert is_valid_continuous_pickup(4) is False

def test_is_valid_continuous_pickup_invalid_types():
    assert is_valid_continuous_pickup(None) is False
    assert is_valid_continuous_pickup("0") is False
    assert is_valid_continuous_pickup(1.0) is False
    assert is_valid_continuous_pickup(True) is False
    assert is_valid_continuous_pickup(["1"]) is False
    assert is_valid_continuous_pickup({"1"}) is False
    assert is_valid_continuous_pickup((1,)) is False