import pytest
from validation_functions.validation_utils import is_valid_fare_attributes_transfers

def test_valid_cemv_support_valid_strings():
    assert is_valid_fare_attributes_transfers("0") is True
    assert is_valid_fare_attributes_transfers("1") is True
    assert is_valid_fare_attributes_transfers("2") is True


def test_valid_cemv_support_invalid_strings():
    assert is_valid_fare_attributes_transfers("-1") is False
    assert is_valid_fare_attributes_transfers("3") is False
    assert is_valid_fare_attributes_transfers("") is False
    assert is_valid_fare_attributes_transfers(" ") is False
    assert is_valid_fare_attributes_transfers("abc") is False
    assert is_valid_fare_attributes_transfers("-") is False
    assert is_valid_fare_attributes_transfers("1.5") is False

def test_valid_cemv_support_invalid_types():
    assert is_valid_fare_attributes_transfers(None) is False
    assert is_valid_fare_attributes_transfers(2) is False
    assert is_valid_fare_attributes_transfers(1.0) is False
    assert is_valid_fare_attributes_transfers(True) is False
    assert is_valid_fare_attributes_transfers(["1"]) is False
    assert is_valid_fare_attributes_transfers({"1"}) is False
    assert is_valid_fare_attributes_transfers((1,)) is False