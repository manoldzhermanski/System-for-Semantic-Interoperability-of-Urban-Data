import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_translations_entity

def test_validate_gtfs_translations_entity_valid():
    """
    Test happy path
    """
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": "Stop_1",
        "field_value": None,
    }

    validate_gtfs_translations_entity(entity)

    assert entity["record_id"] == "urn:ngsi-ld:GtfsStop:Sofia:Stop_1"
    
def test_validate_gtfs_translations_entity_missing_required_field():
    """
    Test that a ValueError is raised when a required field is missing
    """
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "en",
        "record_id": "Stop_1",
        "field_value": None,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_translations_entity(entity)
        
    assert "Missing required GTFS field" in str(err.value)
    
def test_validate_gtfs_translations_entity_invalid_table_name():
    """
    Test that ValueError is raised when 'table_name' field has an invalid value
    """
    entity = {
        "table_name": "invalid-table-name",
        "field_name": "stop_name",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": "Stop_1",
        "field_value": None,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_translations_entity(entity)
        
    assert """'table_name' must be agency, stops, routes, trips, stop_times, pathways, 
                         levels, feed_info, attributions""" in str(err.value)
                         
def test_validate_gtfs_translations_entity_invalid_language():
    """
    Test that ValueError is raised when the 'language' field contains invalid language code
    """
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "not-a-code",
        "translation": "TSentralna gara",
        "record_id": "Stop_1",
        "field_value": None,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_translations_entity(entity)
        
    assert "language must be a valid language code" in str(err.value)
    
def test_validate_gtfs_translations_entity_requires_record_id_or_field_value():
    """
    Test that ValueError is raised when 'record_id' and 'field_value' are mssing at the same time
    """
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": None,
        "field_value": None,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_translations_entity(entity)
        
    assert "Either 'record_id' or 'field_value' has to be defined" in str(err.value)
    
def test_validate_gtfs_translations_entity_stop_times_requires_record_sub_id():
    """
    Test that if 'table_name' is stop_times, 'record_sub_id' has to be defined
    """
    entity = {
        "table_name": "stop_times",
        "field_name": "stop_headsign",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": "Trip_1",
        "record_sub_id": None,
        "field_value": None,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_translations_entity(entity)
        
    assert "'record_sub_id' (stop_sequence) is required when table_name is 'stop_times'" in str(err.value)
    
def test_validate_gtfs_translations_entity_stop_times_valid():
    """
    Test that 'record_id' is transformed when 'record_sub_id' is defined
    """
    entity = {
        "table_name": "stop_times",
        "field_name": "stop_headsign",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": "Trip_1",
        "record_sub_id": 5,
        "field_value": None,
    }

    validate_gtfs_translations_entity(entity)

    assert entity["record_id"] == "urn:ngsi-ld:GtfsTrip:Sofia:Trip_1"