import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_transfers_data

def test_parse_gtfs_transfers_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "transfer_type": "2",
        "min_transfer_time": "300"
    }

    result = parse_gtfs_transfers_data(entity)

    assert result == {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "transfer_type": 2,
        "min_transfer_time": 300
    }

def test_parse_gtfs_transfers_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}

    result = parse_gtfs_transfers_data(entity)

    assert result == {
        "from_stop_id": None,
        "to_stop_id": None,
        "from_route_id": None,
        "to_route_id": None,
        "from_trip_id": None,
        "to_trip_id": None,
        "transfer_type": None,
        "min_transfer_time": None
    }

def test_parse_gtfs_transfers_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "from_stop_id": " S1 ",
        "to_stop_id": " S2 ",
        "transfer_type": " 1 ",
        "min_transfer_time": " 120 "
    }

    result = parse_gtfs_transfers_data(entity)

    assert result == {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_route_id": None,
        "to_route_id": None,
        "from_trip_id": None,
        "to_trip_id": None,
        "transfer_type": 1,
        "min_transfer_time": 120
    }

def test_parse_gtfs_transfers_data_invalid_transfer_type_raises_error():
    """
    Check that if 'transfer_type' cannot be parsed to integer, ValueError is raised
    """
    entity = {"transfer_type": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_transfers_data(entity)

    assert str(err.value) == "transfer_type must be integer, got 'abc'"

def test_parse_gtfs_transfers_data_invalid_min_transfer_time_raises_error():
    """
    Check that if 'min_transfer_time' cannot be parsed to integer, ValueError is raised
    """
    entity = {"min_transfer_time": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_transfers_data(entity)

    assert str(err.value) == "min_transfer_time must be integer, got 'abc'"
