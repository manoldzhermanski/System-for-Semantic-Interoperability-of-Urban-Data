import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_levels_data

def test_parse_gtfs_levels_data_all_fields_present():
    """
    Check if all fields are provided, they are parsed correctly
    """
    entity = {
        "level_id": "L1",
        "level_index": "1.5",
        "level_name": "Platform"
    }

    result = parse_gtfs_levels_data(entity)

    assert result == {
        "level_id": "L1",
        "level_index": 1.5,
        "level_name": "Platform"
    }

def test_parse_gtfs_levels_data_missing_fields():
    """
    Check that if fields are missing, None value is assigned
    """
    entity = {}

    result = parse_gtfs_levels_data(entity)

    assert result == {
        "level_id": None,
        "level_index": None,
        "level_name": None
    }

def test_parse_gtfs_levels_data_whitespace_cleanup():
    """
    Check that whitespaces are trimmed
    """
    entity = {
        "level_id": " L1 ",
        "level_index": " 2.0 ",
        "level_name": " Main Platform "
    }

    result = parse_gtfs_levels_data(entity)

    assert result == {
        "level_id": "L1",
        "level_index": 2.0,
        "level_name": "Main Platform"
    }

def test_parse_gtfs_levels_data_invalid_level_index_raises_error():
    """
    Check that if 'level_index' cannot be parsed to float, ValueError is raised
    """

    entity = {"level_index": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_levels_data(entity)

    assert str(err.value) == "level_index must be float, got 'abc'"
