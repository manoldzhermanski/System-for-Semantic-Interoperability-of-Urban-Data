import pytest
from validation_functions.validation_utils import is_valid_email

def test_is_valid_email_valid_strings():
    assert is_valid_email("test@example.com") is True
    assert is_valid_email("user.name+tag@domain.co") is True
    assert is_valid_email("   test@example.com   ") is True

def test_is_valid_email_invalid_strings():
    assert is_valid_email("") is False
    assert is_valid_email("   ") is False
    assert is_valid_email("invalid") is False
    assert is_valid_email("no-at-symbol.com") is False
    assert is_valid_email("missingdomain@") is False
    assert is_valid_email("@missinguser.com") is False
    assert is_valid_email("test@.com") is False
    assert is_valid_email("test@domain") is False
    
def test_is_valid_url_invalid_types():
    assert is_valid_email(None) is False
    assert is_valid_email(123) is False
    assert is_valid_email(3.14) is False
    assert is_valid_email([]) is False
    assert is_valid_email({}) is False
    assert is_valid_email(()) is False
    assert is_valid_email(True) is False
    