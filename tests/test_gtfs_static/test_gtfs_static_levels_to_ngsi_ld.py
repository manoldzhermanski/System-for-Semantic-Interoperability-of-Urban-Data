import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_levels_to_ngsi_ld

def test_valid_gtfs_levels_conversion():
    """
    Check that if all fields of GTFS Levels are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "level_id": "0",
            "level_index": "8",
            "level_name": "OK"
        }
    ]

    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsLevel:0",
            "type": "GtfsLevel",
            "name": {
                "type": "Property",
                "value": "OK"
            },
            
            "level_index": {
                "type": "Property",
                "value": 8.0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_levels_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_missing_level_id_raises_value_error():
    """
    Check that if the 'level_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'level_id'
    raw_data = [
        {
            "level_index": "8",
            "level_name": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_levels_to_ngsi_ld(raw_data)

def test_missing_level_index_raises_value_error():
    """
    Check that if the 'level_index' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'level_index'
    raw_data = [
        {
            "level_id": "0",
            "level_name": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_levels_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide all required fields with an empty optional field
    raw_data = [
        {
            "level_id": "0",
            "level_index": "8",
            "level_name": ""
        }
    ]

    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsLevel:0",
            "type": "GtfsLevel",
            "level_index": {
                "type": "Property",
                "value": 8.0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_levels_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_multiple_entities():
    """
    Check if the raw data contains 2 entities, 
    after the transformation 2 entites are returned from the function call
    """
    # Provide raw data
    raw_data = [
        {
            "level_id": "0",
            "level_index": "8",
            "level_name": "OK"
        },
        {
            "level_id": "10",
            "level_index": "8",
            "level_name": "OK"
        }
    ]

    # Get result from the function call
    result = gtfs_static_levels_to_ngsi_ld(raw_data)
    
    # Check if 2 entities are returned after the function call
    assert len(result) == 2

def test_unknown_fields_are_ignored():
    """
    Check if an unknown data field is provided,
    it's ignored during the transformation
    """
    # Provide raw data
    raw_data = [
        {
            "level_id": " 0",
            "level_index": "8 ",
            "level_name": " OK ",
            "unknown_field": "unknown_value"
        }
    ]

    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsLevel:0",
            "type": "GtfsLevel",
            "name": {
                "type": "Property",
                "value": "OK"
            },
            
            "level_index": {
                "type": "Property",
                "value": 8
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_levels_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if a field contains white spaces, they are removed
    """
    # Provide raw data
    raw_data = [
        {
            "level_id": " 0",
            "level_index": "8 ",
            "level_name": " OK "
        }
    ]

    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsLevel:0",
            "type": "GtfsLevel",
            "name": {
                "type": "Property",
                "value": "OK"
            },
            
            "level_index": {
                "type": "Property",
                "value": 8
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_levels_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_empty_levels_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_levels_to_ngsi_ld(raw_data)

def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_levels_to_ngsi_ld(raw_data) == []