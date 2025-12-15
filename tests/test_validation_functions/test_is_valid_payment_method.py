import pytest
from validation_functions.validation_utils import is_valid_payment_method

def test_is_valid_payment_method_valid_values():
    assert is_valid_payment_method(0) is True
    assert is_valid_payment_method(1) is True

def test_is_valid_payment_method_invalid_values():
    assert is_valid_payment_method(-1) is False
    assert is_valid_payment_method(2) is False

def test_is_valid_payment_method_invalid_types():
    assert is_valid_payment_method(None) is False
    assert is_valid_payment_method("0") is False
    assert is_valid_payment_method(1.0) is False
    assert is_valid_payment_method(True) is False
    assert is_valid_payment_method(["1"]) is False
    assert is_valid_payment_method({"1"}) is False
    assert is_valid_payment_method((1,)) is False