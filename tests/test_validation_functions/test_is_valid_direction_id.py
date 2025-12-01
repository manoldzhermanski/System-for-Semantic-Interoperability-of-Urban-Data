import pytest
from validation_functions.validation_utils import is_valid_direction_id

def test_is_valid_direction_id_valid_strings():
    assert is_valid_direction_id("0") is True
    assert is_valid_direction_id("1") is True

def test_is_valid_direction_id_invalid_strings():
    assert is_valid_direction_id("-1") is False
    assert is_valid_direction_id("2") is False
    assert is_valid_direction_id("") is False
    assert is_valid_direction_id(" ") is False
    assert is_valid_direction_id("abc") is False
    assert is_valid_direction_id("-") is False
    assert is_valid_direction_id("1.5") is False

def test_is_valid_direction_id_invalid_types():
    assert is_valid_direction_id(None) is False
    assert is_valid_direction_id(2) is False
    assert is_valid_direction_id(1.0) is False
    assert is_valid_direction_id(True) is False
    assert is_valid_direction_id(["1"]) is False
    assert is_valid_direction_id({"1"}) is False
    assert is_valid_direction_id((1,)) is False