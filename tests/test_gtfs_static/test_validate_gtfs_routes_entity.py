import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_routes_entity

def test_validate_gtfs_routes_entity_all_fields_valid():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    validate_gtfs_routes_entity(entity)

def test_validate_gtfs_routes_entity_missing_required_field():
    entity = {
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_routes_entity_none_value_as_required_field():
    entity = {
        "route_id": None,
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_routes_entity_optional_fields_none():
    entity = {
        "route_id": "R1",
        "agency_id": None,
        "route_short_name": None,
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": None,
        "route_color": None,
        "route_text_color": None,
        "route_sort_order": None,
        "continuous_pickup": None,
        "continuous_drop_off": None,
        "network_id": None,
        "cemv_support": None
    }

    validate_gtfs_routes_entity(entity)

def test_validate_gtfs_routes_entity_missing_both_names():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Either 'route_short_name' or 'route_long_name' has to be defined" in str(err.value)

def test_validate_gtfs_routes_entity_route_short_name_too_long():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "ABCDEFGHIJKLMN",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'route_short_name' has to be no longer than 12 characters" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_type():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 10,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'route_type' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_url():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "www.example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Invalid URL for 'route_url'" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_color():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "ZZZZZZ",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Invalid color code for" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_text_color():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "ZZZZZZ",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "Invalid color code for" in str(err.value)

def test_validate_gtfs_routes_entity_negative_sort_order():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": -1,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'route_sort_order' must be a non-negative integer" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_continuous_pickup():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 4,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'continuous_pickup' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_continuous_drop_off():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 4,
        "network_id": "N1",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'continuous_drop_off' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_cemv_support():
    entity = {
        "route_id": "R1",
        "agency_id": "A1",
        "route_short_name": "Metro",
        "route_long_name": "Metro Line 1",
        "route_type": 1,
        "route_url": "https://example.com",
        "route_color": "FFFFFF",
        "route_text_color": "000000",
        "route_sort_order": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 2,
        "network_id": "N1",
        "cemv_support": 3
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity)

    assert "'cemv_support' has to be" in str(err.value)
