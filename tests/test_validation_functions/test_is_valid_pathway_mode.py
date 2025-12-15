import pytest
from validation_functions.validation_utils import is_valid_pathway_mode

def test_is_valid_pathway_mode_valid_values():
    assert is_valid_pathway_mode(1) is True
    assert is_valid_pathway_mode(2) is True
    assert is_valid_pathway_mode(3) is True
    assert is_valid_pathway_mode(4) is True
    assert is_valid_pathway_mode(5) is True
    assert is_valid_pathway_mode(6) is True
    assert is_valid_pathway_mode(7) is True

def test_is_valid_pathway_mode_invalid_values():
    assert is_valid_pathway_mode(0) is False
    assert is_valid_pathway_mode(8) is False
    
def test_is_valid_pathway_mode_invalid_types():
    assert is_valid_pathway_mode(None) is False
    assert is_valid_pathway_mode("1") is False
    assert is_valid_pathway_mode(1.0) is False
    assert is_valid_pathway_mode(True) is False
    assert is_valid_pathway_mode(["1"]) is False
    assert is_valid_pathway_mode({"1"}) is False
    assert is_valid_pathway_mode((1,)) is False