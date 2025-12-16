import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_trips_data

def test_parse_gtfs_trips_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "route_id": "R1",
        "service_id": "SV1",
        "trip_id": "T1",
        "trip_headsign": "Downtown",
        "trip_short_name": "10",
        "direction_id": "1",
        "block_id": "B1",
        "shape_id": "SH1",
        "wheelchair_accessible": "1",
        "bikes_allowed": "2",
        "cars_allowed": "0"
    }

    result = parse_gtfs_trips_data(entity)

    assert result == {
        "route_id": "R1",
        "service_id": "SV1",
        "trip_id": "T1",
        "trip_headsign": "Downtown",
        "trip_short_name": "10",
        "direction_id": 1,
        "block_id": "B1",
        "shape_id": "SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0
    }

def test_parse_gtfs_trips_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}
    result = parse_gtfs_trips_data(entity)

    assert result == {
        "route_id": None,
        "service_id": None,
        "trip_id": None,
        "trip_headsign": None,
        "trip_short_name": None,
        "direction_id": None,
        "block_id": None,
        "shape_id": None,
        "wheelchair_accessible": None,
        "bikes_allowed": None,
        "cars_allowed": None
    }

def test_parse_gtfs_trips_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "route_id": " R1 ",
        "trip_id": " T1 ",
        "direction_id": " 0 ",
        "wheelchair_accessible": " 1 ",
        "bikes_allowed": " 2 ",
        "cars_allowed": " 0 "
    }

    result = parse_gtfs_trips_data(entity)

    assert result == {
        "route_id": "R1",
        "service_id": None,
        "trip_id": "T1",
        "trip_headsign": None,
        "trip_short_name": None,
        "direction_id": 0,
        "block_id": None,
        "shape_id": None,
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0
    }

def test_parse_gtfs_trips_data_invalid_direction_id_raises_error():
    """
    Check that if 'direction_id' cannot be parsed to integer, ValueError is raised
    """
    entity = {"direction_id": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_trips_data(entity)

    assert str(err.value) == "direction_id must be integer, got 'abc'"

def test_parse_gtfs_trips_data_invalid_wheelchair_accessible_raises_error():
    """
    Check that if 'wheelchair_accessible' cannot be parsed to integer, ValueError is raised
    """
    entity = {"wheelchair_accessible": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_trips_data(entity)

    assert str(err.value) == "wheelchair_accessible must be integer, got 'abc'"

def test_parse_gtfs_trips_data_invalid_bikes_allowed_raises_error():
    """
    Check that if 'bikes_allowed' cannot be parsed to integer, ValueError is raised
    """
    entity = {"bikes_allowed": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_trips_data(entity)

    assert str(err.value) == "bikes_allowed must be integer, got 'abc'"

def test_parse_gtfs_trips_data_invalid_cars_allowed_raises_error():
    """
    Check that if 'cars_allowed' cannot be parsed to integer, ValueError is raised
    """
    entity = {"cars_allowed": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_trips_data(entity)

    assert str(err.value) == "cars_allowed must be integer, got 'abc'"
