import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_routes_data

def test_parse_gtfs_routes_data_all_fields_present():
    """
    Check if all fields are provided, they are parsed correctly
    """
    entity = {
        "route_id": "R1",
        "agency_id": "AG1",
        "route_short_name": "10",
        "route_long_name": "Main Street",
        "route_desc": "Description",
        "route_type": "3",
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": "1",
        "continuous_pickup": "0",
        "continuous_drop_off": "0",
        "network_id": "N1",
        "cemv_support": "1"
    }

    result = parse_gtfs_routes_data(entity)

    assert result == {
        "route_id": "R1",
        "agency_id": "AG1",
        "route_short_name": "10",
        "route_long_name": "Main Street",
        "route_desc": "Description",
        "route_type": 3,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 0,
        "network_id": "N1",
        "cemv_support": 1
    }

def test_parse_gtfs_routes_data_missing_fields():
    """
    Check that if fields are missing, None value is assigned
    """
    entity = {}
    result = parse_gtfs_routes_data(entity)

    assert result == {
        "route_id": None,
        "agency_id": None,
        "route_short_name": None,
        "route_long_name": None,
        "route_desc": None,
        "route_type": None,
        "route_url": None,
        "route_color": None,
        "route_text_color": None,
        "route_sort_order": None,
        "continuous_pickup": None,
        "continuous_drop_off": None,
        "network_id": None,
        "cemv_support": None
    }

def test_parse_gtfs_routes_data_whitespace_cleanup():
    """
    Check that whitespaces are trimmed
    """
    entity = {
        "route_id": " R1 ",
        "route_type": " 3 ",
        "route_sort_order": " 1 ",
        "continuous_pickup": " 0 ",
        "continuous_drop_off": " 0 ",
        "cemv_support": " 1 "
    }

    result = parse_gtfs_routes_data(entity)

    assert result == {
        "route_id":"R1",
        "agency_id": None,
        "route_short_name": None,
        "route_long_name": None,
        "route_desc": None,
        "route_type": 3,
        "route_url": None,
        "route_color": None,
        "route_text_color": None,
        "route_sort_order": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 0,
        "network_id": None,
        "cemv_support": 1
    }

def test_parse_gtfs_routes_data_invalid_route_type_raises_error():
    """
    Check that if 'route_type' cannot be parsed to integer, ValueError is raised
    """
    entity = {"route_type": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_routes_data(entity)
    assert str(err.value) == "route_type must be integer, got 'abc'"

def test_parse_gtfs_routes_data_invalid_route_sort_order_raises_error():
    """
    Check that if 'route_sort_order' cannot be parsed to integer, ValueError is raised
    """
    entity = {"route_sort_order": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_routes_data(entity)
    assert str(err.value) == "route_sort_order must be integer, got 'abc'"

def test_parse_gtfs_routes_data_invalid_continuous_pickup_raises_error():
    """
    Check that if 'continuous_pickup' cannot be parsed to integer, ValueError is raised
    """
    entity = {"continuous_pickup": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_routes_data(entity)
    assert str(err.value) == "continuous_pickup must be integer, got 'abc'"

def test_parse_gtfs_routes_data_invalid_continuous_drop_off_raises_error():
    """
    Check that if 'continuous_drop_off' cannot be parsed to integer, ValueError is raised
    """
    entity = {"continuous_drop_off": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_routes_data(entity)
    assert str(err.value) == "continuous_drop_off must be integer, got 'abc'"

def test_parse_gtfs_routes_data_invalid_cemv_support_raises_error():
    """
    Check that if 'cemv_support' cannot be parsed to integer, ValueError is raised
    """
    entity = {"cemv_support": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_routes_data(entity)
    assert str(err.value) == "cemv_support must be integer, got 'abc'"
