import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_stops_entity

def test_validate_gtfs_stops_entity_all_fields_valid():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    validate_gtfs_stops_entity(entity, city)

def test_validate_gtfs_stops_entity_missing_required_field():
    """
    Check that a missing required field raises ValueError
    """
    entity = {
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "Missing required GTFS field: stop_id" in str(err.value)

def test_validate_gtfs_stops_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
    entity = {
        "stop_id": "S1",
        "stop_code": None,
        "stop_name": "Main Stop",
        "tts_stop_name": None,
        "stop_desc": None,
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": None,
        "stop_url": None,
        "location_type": None,
        "parent_station": "STATION_1",
        "stop_timezone": None,
        "wheelchair_boarding": None,
        "level_id": None,
        "platform_code": None,
        "stop_access": 0,
    }
    
    city = "Sofia"

    validate_gtfs_stops_entity(entity, city)

def test_validate_gtfs_stops_entity_invalid_location_type():
    """
    Check that invalid 'location_type' raises ValueError
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 5,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'location_type' must be" in str(err.value)

def test_validate_gtfs_stops_entity_missing_stop_name_for_location_type_0():
    """
    Check that if 'location_type' is 0,1 or 2 and if 'stop_name' is missing, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'stop_name' is required when 'location_type' is 0, 1 or 2" in str(err.value)

def test_validate_gtfs_stops_entity_missing_stop_lat_for_location_type_0():
    """
    Check that if 'location_type' is 0,1 or 2 and if 'stop_lat' is missing, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'stop_lat' is required when 'location_type' is 0, 1 or 2" in str(err.value)

def test_validate_gtfs_stops_entity_missing_stop_lon_for_location_type_0():
    """
    Check that if 'location_type' is 0,1 or 2 and if 'stop_lon' is missing, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'stop_lon' is required when 'location_type' is 0, 1 or 2" in str(err.value)

def test_validate_gtfs_stops_entity_location_type_2_missing_parent_station():
    """
    Check that if 'location_type' is 2, 3 or 4 and if 'parent_station' isn't defined, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 2,
        "parent_station": None,
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'parent_station' is required when 'location_type' is 2, 3 or 4" in str(err.value)

def test_validate_gtfs_stops_entity_location_type_1_parent_station_forbidden():
    """
    Checl that if 'location_type' is 1 and 'parent_station' has a value, ValueError is raised 
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 1,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'parent_station' is forbidden when 'location_type' is 1" in str(err.value)

def test_validate_gtfs_stops_entity_invalid_stop_url():
    """
    Check that invalid value for 'stop_url' raises ValueError
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "not-a-url",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "Invalid URL for" in str(err.value)

def test_validate_gtfs_stops_entity_invalid_stop_timezone():
    """
    Check that invalid value for 'stop_timezone' raises ValueError
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Invalid/Zone",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)

    assert "Invalid timezone for" in str(err.value)
    
def test_validate_gtfs_stops_entity_invalid_wheelchair_boarding():
    """
    Check that invalid value for 'wheelchair_boarding' raises ValueError
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": "STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 3,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 0,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'wheelchair_boarding' must be 0, 1 or 2" in str(err.value)

def test_validate_gtfs_stops_entity_invalid_stop_access_value():
    """
    Check that invalid value for 'stop_access' raises ValueError
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 0,
        "parent_station": None,
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 2,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "'stop_access' must be 0 or 1, got" in str(err.value)

def test_validate_gtfs_stops_entity_stop_access_forbidden_for_location_type_2():
    """
    Check that if 'location_type' is 2,3 or 4, and 'stop_access' has a value, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 2,
        "parent_station": "ST1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 1,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "is forbidden for location_type 2, 3 and 4" in str(err.value)

def test_validate_gtfs_stops_entity_location_type_1_missing_stop_access():
    """
    Check that if 'parent_station' is empty (when 'location_type' is 1) and 'stop_access' has a value, ValueError is raised
    """
    entity = {
        "stop_id": "S1",
        "stop_code": "SC1",
        "stop_name": "Main Stop",
        "tts_stop_name": "Main Stop TTS",
        "stop_desc": "Description",
        "stop_lat": 42.6977,
        "stop_lon": 23.3219,
        "zone_id": "Z1",
        "stop_url": "https://example.com/stop",
        "location_type": 1,
        "parent_station": None,
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "L1",
        "platform_code": "1A",
        "stop_access": 1,
    }
    
    city = "Sofia"

    with pytest.raises(ValueError, match="stop_access") as err:
        validate_gtfs_stops_entity(entity, city)
        
    assert "is forbidden when 'parent_station' is empty" in str(err.value)
