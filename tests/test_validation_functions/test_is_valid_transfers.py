import pytest
from validation_functions.validation_utils import is_valid_transfers

def test_is_valid_transfers_valid_values():
    assert is_valid_transfers(-1) is True
    assert is_valid_transfers(0) is True
    assert is_valid_transfers(1) is True
    assert is_valid_transfers(2) is True

def test_is_valid_transfers_invalid_values():
    assert is_valid_transfers(-2) is False
    assert is_valid_transfers(3) is False
    
def test_is_valid_transfers_invalid_types():
    assert is_valid_transfers(None) is False
    assert is_valid_transfers("0") is False
    assert is_valid_transfers(1.0) is False
    assert is_valid_transfers(True) is False
    assert is_valid_transfers(["1"]) is False
    assert is_valid_transfers({"1"}) is False
    assert is_valid_transfers((1,)) is False