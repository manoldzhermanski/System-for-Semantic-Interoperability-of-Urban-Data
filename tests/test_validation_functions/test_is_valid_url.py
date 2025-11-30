import pytest
from validation_functions.validation_utils import is_valid_url

def test_is_valid_url_valid_strings():
    assert is_valid_url("http://example.com") is True
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("   https://example.com   ") is True
    assert is_valid_url("https://example.com:8080") is True
    assert is_valid_url("http://127.0.0.1") is True
    assert is_valid_url("https://example.com/path/to/page?query=123&x=5") is True

def test_is_valid_url_invalid_strings():
    assert is_valid_url("") is False
    assert is_valid_url("   ") is False
    assert is_valid_url("www.example.com") is False
    assert is_valid_url("not a url") is False
    assert is_valid_url("http//missingcolon.com") is False
    assert is_valid_url("https:/one-slash.com") is False
    assert is_valid_url("http://") is False
    assert is_valid_url("://missing.scheme.com") is False
    
def test_is_valid_url_invalid_types():
    assert is_valid_url(None) is False
    assert is_valid_url(123) is False
    assert is_valid_url(3.14) is False
    assert is_valid_url([]) is False
    assert is_valid_url({}) is False
    assert is_valid_url(()) is False
    assert is_valid_url(True) is False