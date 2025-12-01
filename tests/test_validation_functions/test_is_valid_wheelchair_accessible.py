import pytest
from validation_functions.validation_utils import is_valid_wheelchair_accessible

def test_is_valid_wheelchair_accessible_valid_strings():
    assert is_valid_wheelchair_accessible("0") is True
    assert is_valid_wheelchair_accessible("1") is True
    assert is_valid_wheelchair_accessible("2") is True

def test_is_valid_wheelchair_accessible_invalid_strings():
    assert is_valid_wheelchair_accessible("-1") is False
    assert is_valid_wheelchair_accessible("3") is False
    assert is_valid_wheelchair_accessible("") is False
    assert is_valid_wheelchair_accessible(" ") is False
    assert is_valid_wheelchair_accessible("abc") is False
    assert is_valid_wheelchair_accessible("-") is False
    assert is_valid_wheelchair_accessible("1.5") is False

def test_is_valid_wheelchair_accessible_invalid_types():
    assert is_valid_wheelchair_accessible(None) is False
    assert is_valid_wheelchair_accessible(2) is False
    assert is_valid_wheelchair_accessible(1.0) is False
    assert is_valid_wheelchair_accessible(True) is False
    assert is_valid_wheelchair_accessible(["1"]) is False
    assert is_valid_wheelchair_accessible({"1"}) is False
    assert is_valid_wheelchair_accessible((1,)) is False