import pytest
from validation_functions.validation_utils import is_valid_language_code

def test_is_valid_language_code_valid_string():
    assert is_valid_language_code("en") is True
    assert is_valid_language_code(" bg ") is True
    assert is_valid_language_code("deu") is True

def test_is_valid_language_code_invalid_string():
    assert is_valid_language_code("") is False
    assert is_valid_language_code("   ") is False
    assert is_valid_language_code("EN") is False
    assert is_valid_language_code("a") is False
    assert is_valid_language_code("ac") is False
    assert is_valid_language_code("xxx") is False
    assert is_valid_language_code("abcd") is False
    assert is_valid_language_code("1n") is False
    assert is_valid_language_code("12") is False
    assert is_valid_language_code("eN") is False
    pass

def test_is_valid_language_code_invalid_type():
    assert is_valid_language_code(None) is False
    assert is_valid_language_code(123) is False
    assert is_valid_language_code(["bg"]) is False
    assert is_valid_language_code({"bg"}) is False

