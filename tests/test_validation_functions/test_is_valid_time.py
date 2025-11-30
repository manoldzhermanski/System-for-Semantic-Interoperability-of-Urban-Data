import pytest
from validation_functions.validation_utils import is_valid_time

def test_is_valid_time_valid_strings():
    assert is_valid_time("00:00:00") is True
    assert is_valid_time("23:59:59") is True
    assert is_valid_time(" 12:34:56 ") is True
    
def test_is_valid_time_invalid_strings():
    assert is_valid_time("") is False
    assert is_valid_time("   ") is False
    assert is_valid_time("24:00:00") is False
    assert is_valid_time("12:60:00") is False
    assert is_valid_time("12:59:60") is False
    assert is_valid_time("123:00:00") is False
    assert is_valid_time("12:00") is False
    assert is_valid_time("12-00-00") is False
    assert is_valid_time("aa:bb:cc") is False
    assert is_valid_time("12:3:00") is False
    assert is_valid_time("12:03:0") is False
    assert is_valid_time("::") is False
    assert is_valid_time("12::00") is False

def test_is_valid_time_invalid_type():
    assert is_valid_time(None) is False
    assert is_valid_time(123) is False
    assert is_valid_time(12.5) is False
    assert is_valid_time([]) is False
    assert is_valid_time({}) is False