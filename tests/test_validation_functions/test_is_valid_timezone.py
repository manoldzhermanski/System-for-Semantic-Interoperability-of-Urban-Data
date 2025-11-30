import pytest
from validation_functions.validation_utils import is_valid_timezone

def test_is_valid_timezones_valid_strings():
    assert is_valid_timezone("Europe/Sofia") is True
    assert is_valid_timezone("UTC") is True
    assert is_valid_timezone(" Europe/Sofia ") is True

def test_is_valid_timezones_invalid_strings():
    assert is_valid_timezone("") is False
    assert is_valid_timezone("  ") is False
    assert is_valid_timezone("Europe/Bulgaria") is False
    assert is_valid_timezone("Invalid/Zone") is False
    assert is_valid_timezone("Sofia") is False
    assert is_valid_timezone("Europe/") is False

def test_is_valid_timezone_invalid_type():
    assert is_valid_timezone(None) is False
    assert is_valid_timezone(123) is False
    assert is_valid_timezone(["Europe/Bulgaria"]) is False
    assert is_valid_timezone({"value": "Europe/Bulgaria"}) is False
    assert is_valid_timezone(("Europe/Bulgaria")) is False