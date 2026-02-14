import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_routes_entity

def test_validate_gtfs_routes_entity_all_fields_valid():
    """
    Check that all fields are provided and valid, the validation passes
    """
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
    
    city = "Sofia"

    validate_gtfs_routes_entity(entity, city)

def test_validate_gtfs_routes_entity_missing_required_field():
    """
    Check that if a required field is missing, ValueError is raised
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_routes_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
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
    
    city = "Sofia"

    validate_gtfs_routes_entity(entity, city)

def test_validate_gtfs_routes_entity_missing_both_names():
    """
    Check that if 'route_short_name' and 'route_long_name' are missing, ValueError is raised
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "Either 'route_short_name' or 'route_long_name' has to be defined" in str(err.value)

def test_validate_gtfs_routes_entity_route_short_name_too_long():
    """
    Check that if 'route_short_name' is longer than 12 characters, ValueError is raised
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'route_short_name' has to be no longer than 12 characters" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_type():
    """
    Check that invalid value for 'route_type' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'route_type' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_url():
    """
    Check that invalid UEL for 'route_url' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "Invalid URL for 'route_url'" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_color():
    """
    Check that invalid color code for 'route_color' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "Invalid color code for" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_route_text_color():
    """
    Check that invalid color code for 'route_text_color' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "Invalid color code for" in str(err.value)

def test_validate_gtfs_routes_entity_negative_sort_order():
    """
    Check that if 'route_sort_order' is not a non-negative integer, ValueError is raised
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'route_sort_order' must be a non-negative integer" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_continuous_pickup():
    """
    Check that invalid value for 'continuous_pickup' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'continuous_pickup' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_continuous_drop_off():
    """
    Check that invalid value for 'continuous_drop_off' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'continuous_drop_off' has to be" in str(err.value)

def test_validate_gtfs_routes_entity_invalid_cemv_support():
    """
    Check that invalid value for 'cemv_support' raises ValueError
    """
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
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_routes_entity(entity, city)

    assert "'cemv_support' has to be" in str(err.value)
