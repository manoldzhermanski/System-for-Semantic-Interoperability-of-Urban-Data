import pytest
from validation_functions.validation_utils import is_valid_route_type

def test_is_valid_route_type_valid_strings():
    assert is_valid_route_type("0") is True
    assert is_valid_route_type("1") is True
    assert is_valid_route_type("2") is True
    assert is_valid_route_type("3") is True
    assert is_valid_route_type("4") is True
    assert is_valid_route_type("5") is True
    assert is_valid_route_type("6") is True
    assert is_valid_route_type("7") is True
    assert is_valid_route_type("11") is True
    assert is_valid_route_type("12") is True

def test_is_valid_route_type_invalid_strings():
    assert is_valid_route_type("-1") is False
    assert is_valid_route_type("8") is False
    assert is_valid_route_type("9") is False
    assert is_valid_route_type("10") is False
    assert is_valid_route_type("13") is False
    assert is_valid_route_type("") is False
    assert is_valid_route_type(" ") is False
    assert is_valid_route_type("abc") is False
    assert is_valid_route_type("-") is False
    assert is_valid_route_type("1.5") is False

def test_is_valid_route_type_invalid_types():
    assert is_valid_route_type(None) is False
    assert is_valid_route_type(2) is False
    assert is_valid_route_type(1.0) is False
    assert is_valid_route_type(True) is False
    assert is_valid_route_type(["1"]) is False
    assert is_valid_route_type({"1"}) is False
    assert is_valid_route_type((1,)) is False