from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_clean_empty_values

def test_gtfs_realtime_clean_empty_values_none_returns_none():
    """
    Check that if the data structure to be pruned is None, None is returned
    """
    assert gtfs_realtime_clean_empty_values(None) is None
    
def test_gtfs_realtime_clean_empty_values_empty_list_returns_none():
    """
    Check that if the data structure to be pruned is an empty list, None is returned
    """
    assert gtfs_realtime_clean_empty_values([]) is None

def test_gtfs_realtime_clean_empty_values_empty_dict_returns_none():
    """
    Check that if the data structure to be pruned is an empty dictionary, None is returned
    """
    assert gtfs_realtime_clean_empty_values({}) is None

def test_gtfs_realtime_clean_empty_values_primitive_values_are_returned_unchanged():
    """
    Check that non-collection values are returned unchanged
    """
    assert gtfs_realtime_clean_empty_values(1) == 1
    assert gtfs_realtime_clean_empty_values("text") == "text"
    assert gtfs_realtime_clean_empty_values(False) is False

def test_gtfs_realtime_clean_empty_values_prune_list_items():
    """
    Check that None values, empty lists and dictionaries are removed from lists
    """
    value = [None, [], {}, 1, "a"]

    result = gtfs_realtime_clean_empty_values(value)

    assert result == [1, "a"]

def test_gtfs_realtime_clean_empty_values_prune_dictionary_entries():
    """
    Check that None values, empty lists and dictionaries are removed from dictionaries
    """
    value = {
        "a": None,
        "b": {},
        "c": [],
        "d": "a",
        "e": 1,
    }

    result = gtfs_realtime_clean_empty_values(value)

    assert result == {"d": "a", "e": 1}

def test_gtfs_realtime_clean_empty_values_prune_nested_structures():
    """
    Check that nested data structures are pruned
    """
    value = {
        "a": {
            "b": "123",
            "c": None,
            "d": [1, "a", None],
        },
        "e": {},
    }

    result = gtfs_realtime_clean_empty_values(value)

    assert result == {
        "a": {
            "b": "123",
            "d": [1, "a"],
        }
    }

def test_gtfs_realtime_clean_empty_values_prune_all():
    """
    Check that if all entries of the data structure are pruned out, a None value is removed
    """
    value = {
        "a": None,
        "b": [],
        "c": {},
    }

    assert gtfs_realtime_clean_empty_values(value) is None
