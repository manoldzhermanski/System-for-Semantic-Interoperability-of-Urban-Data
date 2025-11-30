import pytest
from validation_functions.validation_utils import is_valid_fare_attributes_payment_method

def test_valid_cemv_support_valid_strings():
    assert is_valid_fare_attributes_payment_method("0") is True
    assert is_valid_fare_attributes_payment_method("1") is True

def test_valid_cemv_support_invalid_strings():
    assert is_valid_fare_attributes_payment_method("-1") is False
    assert is_valid_fare_attributes_payment_method("2") is False
    assert is_valid_fare_attributes_payment_method("") is False
    assert is_valid_fare_attributes_payment_method(" ") is False
    assert is_valid_fare_attributes_payment_method("abc") is False
    assert is_valid_fare_attributes_payment_method("-") is False
    assert is_valid_fare_attributes_payment_method("1.5") is False

def test_valid_cemv_support_invalid_types():
    assert is_valid_fare_attributes_payment_method(None) is False
    assert is_valid_fare_attributes_payment_method(2) is False
    assert is_valid_fare_attributes_payment_method(1.0) is False
    assert is_valid_fare_attributes_payment_method(True) is False
    assert is_valid_fare_attributes_payment_method(["1"]) is False
    assert is_valid_fare_attributes_payment_method({"1"}) is False
    assert is_valid_fare_attributes_payment_method((1,)) is False