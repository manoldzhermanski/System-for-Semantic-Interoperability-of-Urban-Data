import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_pathways_data

def test_parse_gtfs_pathways_data_all_fields_present():
    """
    Check if all fields are provided, they are parsed correctly
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": "1",
        "is_bidirectional": "0",
        "length": "10.5",
        "traversal_time": "120",
        "stair_count": "3",
        "max_slope": "0.05",
        "min_width": "1.2",
        "signposted_as": "Main",
        "reversed_signposted_as": "Back"
    }

    result = parse_gtfs_pathways_data(entity)

    assert result == {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 120,
        "stair_count": 3,
        "max_slope": 0.05,
        "min_width": 1.2,
        "signposted_as": "Main",
        "reversed_signposted_as": "Back"
    }

def test_parse_gtfs_pathways_data_missing_fields():
    """
    Check that if fields are missing, None value is assigned
    """
    entity = {}
    result = parse_gtfs_pathways_data(entity)

    assert result == {
        "pathway_id": None,
        "from_stop_id": None,
        "to_stop_id": None,
        "pathway_mode": None,
        "is_bidirectional": None,
        "length": None,
        "traversal_time": None,
        "stair_count": None,
        "max_slope": None,
        "min_width": None,
        "signposted_as": None,
        "reversed_signposted_as": None
    }

def test_parse_gtfs_pathways_data_whitespace_cleanup():
    """
    Check that whitespaces are trimmed
    """
    entity = {
        "pathway_id": " P1 ",
        "length": " 10.5 ",
        "traversal_time": " 120 ",
        "signposted_as": " Main ",
    }

    result = parse_gtfs_pathways_data(entity)

    assert result == {
        "pathway_id": "P1",
        "from_stop_id": None,
        "to_stop_id": None,
        "pathway_mode": None,
        "is_bidirectional": None,
        "length":10.5,
        "traversal_time": 120,
        "stair_count": None,
        "max_slope": None,
        "min_width": None,
        "signposted_as": "Main",
        "reversed_signposted_as": None
    }

def test_parse_gtfs_pathways_data_invalid_pathway_mode_raises_error():
    """
    Check that if 'pathway_mode' cannot be parsed to integer, ValueError is raised
    """
    entity = {"pathway_mode": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "pathway_mode must be integer, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_is_bidirectional_raises_error():
    """
    Check that if 'is_bidirectional' cannot be parsed to integer, ValueError is raised
    """
    entity = {"is_bidirectional": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "is_bidirectional must be integer, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_traversal_time_raises_error():
    """
    Check that if 'traversal_time' cannot be parsed to integer, ValueError is raised
    """
    entity = {"traversal_time": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "traversal_time must be integer, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_stair_count_raises_error():
    """
    Check that if 'stair_count' cannot be parsed to integer, ValueError is raised
    """
    entity = {"stair_count": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "stair_count must be integer, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_length_raises_error():
    """
    Check that if 'length' cannot be parsed to float, ValueError is raised
    """
    entity = {"length": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "length must be float, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_max_slope_raises_error():
    """
    Check that if 'max_slope' cannot be parsed to float, ValueError is raised
    """
    entity = {"max_slope": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "max_slope must be float, got 'abc'"

def test_parse_gtfs_pathways_data_invalid_min_width_raises_error():
    """
    Check that if 'min_width' cannot be parsed to float, ValueError is raised
    """
    entity = {"min_width": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_pathways_data(entity)
    assert str(err.value) == "min_width must be float, got 'abc'"

