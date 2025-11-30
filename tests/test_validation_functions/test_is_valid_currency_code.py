import pytest
from validation_functions.validation_utils import is_valid_currency_code

def test_is_valid_currency_code_valid_string():
    assert is_valid_currency_code("USD") is True
    assert is_valid_currency_code("EUR") is True
    assert is_valid_currency_code("BGN") is True
    assert is_valid_currency_code(" BGN ") is True


def test_is_valid_currency_code_invalid_strings():
    assert is_valid_currency_code("") is False
    assert is_valid_currency_code("   ") is False
    assert is_valid_currency_code("A") is False
    assert is_valid_currency_code("AB") is False
    assert is_valid_currency_code("ABCD") is False
    assert is_valid_currency_code("ABCDE") is False
    assert is_valid_currency_code("AAA") is False
    assert is_valid_currency_code("123") is False
    assert is_valid_currency_code("A1C") is False
    assert is_valid_currency_code("usd") is False
    assert is_valid_currency_code(" Eur ") is False
    assert is_valid_currency_code("bGn") is False
    
def test_is_valid_currency_code_invalid_type():
    assert is_valid_currency_code(None) is False
    assert is_valid_currency_code(123) is False
    assert is_valid_currency_code(["BGN"]) is False
    assert is_valid_currency_code({"value": "BGN"}) is False
