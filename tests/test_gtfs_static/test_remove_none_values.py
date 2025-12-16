import pytest
from gtfs_static.gtfs_static_utils import remove_none_values

def test_remove_none_values_no_nested_dicts():
    """
    Check that if that entities with values which non-dictionary values are not removed
    """
    entity = {
        "a": 1,
        "b": None,
        "c": "text"
    }

    result = remove_none_values(entity)

    assert result == entity

def test_remove_none_values_mixed_nested_dicts():
    """
    Check that if a nested dict has a None-value, the key-nested dict as value pair is removed
    """
    entity = {
        "keep": {"a": 1},
        "remove": {"a": None},
        "value": 42
    }

    result = remove_none_values(entity)

    assert result == {
        "keep": {"a": 1},
        "value": 42
    }

def test_remove_none_values_nested_dict_with_none_is_removed():
    """
    Check that if in the nested dict there is a key-value pair with a None value,
    the key-nested dict as a value pair is removed
    """
    entity = {
        "a": {"x": 1, "y": None},
        "b": 2
    }

    result = remove_none_values(entity)

    assert result == {
        "b": 2
    }

def test_remove_none_values_nested_dict_without_none_is_kept():
    """
    Check that if the nested dict isn't a None value, the key - dict as value pair is kept
    """
    entity = {
        "a": {"x": 1, "y": 2},
        "b": 3
    }

    result = remove_none_values(entity)

    assert result == entity

def test_remove_none_values_empty_dict():
    """
    Check that if empty dict is given as input, empty dict is returned
    """
    assert remove_none_values({}) == {}

