import pytest
from validation_functions.validation_utils import is_string

def test_is_string_valid_strings():
    assert is_string("hello") is True
    assert is_string("") is True
    assert is_string("123") is True
    assert is_string(" ") is True
    assert is_string("текст") is True

def test_is_string_invalid_types():
    assert is_string(123) is False
    assert is_string(12.5) is False
    assert is_string(True) is False
    assert is_string(None) is False
    assert is_string(["a", "b"]) is False
    assert is_string({"a": 1}) is False
    assert is_string(('a',)) is False
    assert is_string(b"bytes") is False 
