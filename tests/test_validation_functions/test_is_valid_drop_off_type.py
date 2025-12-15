import pytest
from validation_functions.validation_utils import is_valid_drop_off_type

def test_is_valid_drop_off_type_valid_values():
    assert is_valid_drop_off_type(0) is True
    assert is_valid_drop_off_type(1) is True
    assert is_valid_drop_off_type(2) is True
    assert is_valid_drop_off_type(3) is True

def test_is_valid_drop_off_type_invalid_values():
    assert is_valid_drop_off_type(-1) is False
    assert is_valid_drop_off_type(4) is False

def test_is_valid_drop_off_type_invalid_types():
    assert is_valid_drop_off_type(None) is False
    assert is_valid_drop_off_type("0") is False
    assert is_valid_drop_off_type(1.0) is False
    assert is_valid_drop_off_type(True) is False
    assert is_valid_drop_off_type(["1"]) is False
    assert is_valid_drop_off_type({"1"}) is False
    assert is_valid_drop_off_type((1,)) is False