import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_stops_data

def test_parse_gtfs_stops_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "100",
        "stop_name": "Central",
        "tts_stop_name": "Central Station",
        "stop_desc": "Main stop",
        "stop_lat": "42.6977",
        "stop_lon": "23.3219",
        "zone_id": "Z1",
        "stop_url": "https://example.com",
        "location_type": "0",
        "parent_station": "PS1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": "1",
        "level_id": "L1",
        "platform_code": "P1",
        "stop_access": "2"
    }

    result = parse_gtfs_stops_data(entity)

    assert result == {
        "stop_id": "S1",
        "stop_code": "100",
        "stop_name": "Central",
        "tts_stop_name": "Central Station",
        "stop_desc": "Main stop",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com",
        "location_type": 0,
        "parent_station": "PS1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "P1",
        "stop_access": 2
    }

def test_parse_gtfs_stops_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}

    result = parse_gtfs_stops_data(entity)

    assert result == {
        "stop_id": None,
        "stop_code": None,
        "stop_name": None,
        "tts_stop_name": None,
        "stop_desc": None,
        "stop_lat": None,
        "stop_lon": None,
        "zone_id": None,
        "stop_url": None,
        "location_type": None,
        "parent_station": None,
        "stop_timezone": None,
        "wheelchair_boarding": None,
        "level_id": None,
        "platform_code": None,
        "stop_access": None
    }

def test_parse_gtfs_stops_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "stop_id": " S1 ",
        "stop_name": " Central ",
        "stop_lat": " 42.6977 ",
        "stop_lon": " 23.3219 ",
        "location_type": " 0 ",
        "wheelchair_boarding": " 1 ",
        "stop_access": " 2 "
    }

    result = parse_gtfs_stops_data(entity)

    assert result == {
        "stop_id": "S1",
        "stop_code": None,
        "stop_name": "Central",
        "tts_stop_name": None,
        "stop_desc": None,
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": None,
        "stop_url": None,
        "location_type": 0,
        "parent_station": None,
        "stop_timezone": None,
        "wheelchair_boarding": 1,
        "level_id": None,
        "platform_code": None,
        "stop_access": 2
    }

def test_parse_gtfs_stops_data_invalid_stop_lat_raises_error():
    """
    Check that if 'stop_lat' cannot be parsed to float, ValueError is raised
    """
    entity = {"stop_lat": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stops_data(entity)
    assert str(err.value) == "stop_lat must be float, got 'abc'"

def test_parse_gtfs_stops_data_invalid_stop_lon_raises_error():
    """
    Check that if 'stop_lon' cannot be parsed to float, ValueError is raised
    """
    entity = {"stop_lon": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stops_data(entity)
    assert str(err.value) == "stop_lon must be float, got 'abc'"

def test_parse_gtfs_stops_data_invalid_location_type_raises_error():
    """
    Check that if 'location_type' cannot be parsed to integer, ValueError is raised
    """
    entity = {"location_type": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stops_data(entity)
    assert str(err.value) == "location_type must be integer, got 'abc'"

def test_parse_gtfs_stops_data_invalid_wheelchair_boarding_raises_error():
    """
    Check that if 'wheelchair_boarding' cannot be parsed to integer, ValueError is raised
    """
    entity = {"wheelchair_boarding": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stops_data(entity)
    assert str(err.value) == "wheelchair_boarding must be integer, got 'abc'"

def test_parse_gtfs_stops_data_invalid_stop_access_raises_error():
    """
    Check that if 'stop_access' cannot be parsed to integer, ValueError is raised
    """
    entity = {"stop_access": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stops_data(entity)
    assert str(err.value) == "stop_access must be integer, got 'abc'"
