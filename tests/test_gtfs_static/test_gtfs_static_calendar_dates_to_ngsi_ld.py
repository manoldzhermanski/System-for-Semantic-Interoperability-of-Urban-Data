import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_calendar_dates_to_ngsi_ld

def test_valid_gtfs_calendar_dates_conversion():
    """
    Check that if all fields of GTFS Calendar Dates are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "service_id": "Sofia_1",
            "date": "20251127",
            "exception_type": "1"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:Sofia:Sofia_1:2025-11-27",
            "type": "GtfsCalendarDateRule",
            
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia_1"
            },
            
            "appliesOn": {
                "type": "Property",
                "value": "2025-11-27"
            },
            
            "exceptionType": {
                "type": "Property",
                "value": 1
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_calendar_dates_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
        
def test_missing_service_id_raises_value_error():
    pass
    """
    Check that if the 'service_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'service_id'
    raw_data = [
        {
            "date": "20251127",
            "exception_type": "1"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_calendar_dates_to_ngsi_ld(raw_data)

def test_missing_date_raises_value_error():
    pass
    """
    Check that if the 'date' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'date'
    raw_data = [
        {
            "service_id": "Sofia_1",
            "exception_type": "1"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_calendar_dates_to_ngsi_ld(raw_data)

def test_missing_exception_type_raises_value_error():
    """
    Check that if the 'exception_type' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'exception_type'
    raw_data = [
        {
            "service_id": "Sofia_1",
            "date": "20251127",
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_calendar_dates_to_ngsi_ld(raw_data)

def test_multiple_entities():
    """
    Check if the raw data contains 2 entities, 
    after the transformation 2 entites are returned from the function call
    """
    # Provide 2 entities
    raw_data = [
        {
            "service_id": "Sofia_1",
            "date": "20251127",
            "exception_type": "1"
        },
        {
            "service_id": "Sofia_2",
            "date": "20251128",
            "exception_type": "2"
        }
    ]
    
    # Get result from the function call
    result = gtfs_static_calendar_dates_to_ngsi_ld(raw_data)
    
    # Check if 2 entities are returned after the function call
    assert len(result) == 2

def test_unknown_fields_are_ignored():
    """
    Check if an unknown data field is provided,
    it's ignored during the transformation
    """
    # Provide data with unknown field
    raw_data = [
        {
            "service_id": "Sofia_1",
            "date": "20251127",
            "exception_type": "1",
            "unkown_field": "unknown_value"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:Sofia:Sofia_1:2025-11-27",
            "type": "GtfsCalendarDateRule",
            
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia_1"
            },
            
            "appliesOn": {
                "type": "Property",
                "value": "2025-11-27"
            },
            
            "exceptionType": {
                "type": "Property",
                "value": 1
            }
        }
    ]
    
    result = gtfs_static_calendar_dates_to_ngsi_ld(raw_data)
    
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the a field contains white spaces, they will be removed
    """
    # Provide all required fields with an optional field whith a white space as a value
    raw_data = [
        {
            "service_id": "Sofia 1",
            "date": " 20251127 ",
            "exception_type": "  1 "
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:Sofia:Sofia 1:2025-11-27",
            "type": "GtfsCalendarDateRule",
            
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia 1"
            },
            
            "appliesOn": {
                "type": "Property",
                "value": "2025-11-27"
            },
            
            "exceptionType": {
                "type": "Property",
                "value": 1
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_calendar_dates_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
     
def test_empty_calendar_dates_dict_raises_error():
    pass
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_calendar_dates_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_calendar_dates_to_ngsi_ld(raw_data) == []