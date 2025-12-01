import pytest
from validation_functions.validation_utils import is_valid_cemv_support

def test_is_valid_cemv_support_valid_strings():
    assert is_valid_cemv_support("0") is True
    assert is_valid_cemv_support("1") is True
    assert is_valid_cemv_support("2") is True

def test_is_valid_cemv_support_invalid_strings():
    assert is_valid_cemv_support("-1") is False
    assert is_valid_cemv_support("3") is False
    assert is_valid_cemv_support("") is False
    assert is_valid_cemv_support(" ") is False
    assert is_valid_cemv_support("abc") is False
    assert is_valid_cemv_support("-") is False
    assert is_valid_cemv_support("1.5") is False

def test_is_valid_cemv_support_invalid_types():
    assert is_valid_cemv_support(None) is False
    assert is_valid_cemv_support(2) is False
    assert is_valid_cemv_support(1.0) is False
    assert is_valid_cemv_support(True) is False
    assert is_valid_cemv_support(["1"]) is False
    assert is_valid_cemv_support({"1"}) is False
    assert is_valid_cemv_support((1,)) is False