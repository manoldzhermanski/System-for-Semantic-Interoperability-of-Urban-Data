import pytest
from validation_functions.validation_utils import is_valid_phone_number

def test_is_valid_phone_numbers_valid_strings():
    assert is_valid_phone_number("0899123456") is True
    assert is_valid_phone_number("+359 899 123 456") is True
    assert is_valid_phone_number("503-238-RIDE") is True
    assert is_valid_phone_number("(02) 123 456") is True
    assert is_valid_phone_number("123/4567") is True
    assert is_valid_phone_number("555-ABCD") is True
    assert is_valid_phone_number("   0899 123 456   ") is True


def test_is_valid_email_invalid_strings():
    assert is_valid_phone_number("") is False
    assert is_valid_phone_number("   ") is False
    assert is_valid_phone_number("abcdEFG") is False
    assert is_valid_phone_number("+++++") is False
    assert is_valid_phone_number("0899*123") is False
    assert is_valid_phone_number("123@456") is False
    assert is_valid_phone_number("call-me!") is False
    assert is_valid_phone_number("123_456") is False

def test_is_valid_phone_number_invalid_types():
    assert is_valid_phone_number(None) is False
    assert is_valid_phone_number(123) is False
    assert is_valid_phone_number(3.14) is False
    assert is_valid_phone_number([]) is False
    assert is_valid_phone_number({}) is False
    assert is_valid_phone_number(()) is False
    assert is_valid_phone_number(True) is False