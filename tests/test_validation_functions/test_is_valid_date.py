import pytest
from validation_functions.validation_utils import is_valid_date

def test_is_valid_date_valid_strings():
    assert is_valid_date("20240101") is True
    assert is_valid_date("19991231") is True
    assert is_valid_date("20240229") is True
    assert is_valid_date(" 20240101 ") is True

def test_is_valid_date_invalid_strings():
    assert is_valid_date("") is False
    assert is_valid_date("   ") is False
    assert is_valid_date("20530230") is False
    assert is_valid_date("20531301") is False
    assert is_valid_date("20530010") is False
    assert is_valid_date("20530100") is False
    assert is_valid_date("20251") is False
    assert is_valid_date("202501011") is False
    assert is_valid_date("2025-01-01") is False
    assert is_valid_date("01/01/2025") is False
    assert is_valid_date("01.01.2025") is False
    assert is_valid_date("2025.01.01") is False
    assert is_valid_date("January 1 2023") is False
    assert is_valid_date("abcdefgh") is False
    assert is_valid_date("2023AA12") is False
    assert is_valid_date("20$40101") is False

def test_is_valid_date_invalid_types():
    assert is_valid_date(None) is False
    assert is_valid_date(20240101) is False
    assert is_valid_date(["20240101"]) is False
    assert is_valid_date({"date": "20240101"}) is False
