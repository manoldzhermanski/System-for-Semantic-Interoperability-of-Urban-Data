import pytest
from validation_functions.validation_utils import is_valid_calendar_date_exception_type

def test_valid_cemv_support_valid_strings():
    assert is_valid_calendar_date_exception_type("1") is True
    assert is_valid_calendar_date_exception_type("2") is True

def test_valid_cemv_support_invalid_strings():
    assert is_valid_calendar_date_exception_type("0") is False
    assert is_valid_calendar_date_exception_type("3") is False
    assert is_valid_calendar_date_exception_type("") is False
    assert is_valid_calendar_date_exception_type(" ") is False
    assert is_valid_calendar_date_exception_type("abc") is False
    assert is_valid_calendar_date_exception_type("-") is False
    assert is_valid_calendar_date_exception_type("1.5") is False

def test_valid_cemv_support_invalid_types():
    assert is_valid_calendar_date_exception_type(None) is False
    assert is_valid_calendar_date_exception_type(2) is False
    assert is_valid_calendar_date_exception_type(1.0) is False
    assert is_valid_calendar_date_exception_type(True) is False
    assert is_valid_calendar_date_exception_type(["1"]) is False
    assert is_valid_calendar_date_exception_type({"1"}) is False
    assert is_valid_calendar_date_exception_type((1,)) is False