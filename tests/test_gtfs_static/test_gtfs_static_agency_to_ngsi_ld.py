import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_agency_to_ngsi_ld

def test_valid_gtfs_agency_conversion():
    """
    Check that if all fields of GTFS Agency are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
        "agency_id": "A1",
        "agency_name": "Agency A1",
        "agency_url": "https://wwww.fakeurl.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "bg",
        "agency_phone": "0899999999",
        "agency_fare_url": "https://www.anotherfakeurl.com",
        "agency_email": "fakeemail@gtfs.com",
        "cemv_support": "1",
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:A1",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": "Agency A1"
            },
                        
            "agency_url": {
                "type": "Property", 
                "value": "https://wwww.fakeurl.com"
            },
            
            "agency_timezone": {
                "type": "Property", 
                "value": "Europe/Sofia"
            },
            
            "agency_lang": {
                "type": "Property", 
                "value": "bg"
            },
            
            "agency_phone": {
                "type": "Property", 
                "value": "0899999999"
            },
            
            "agency_fare_url": {
                "type": "Property",
                "value": "https://www.anotherfakeurl.com"
            },
            
            "agency_email": {
                "type": "Property", 
                "value": "fakeemail@gtfs.com"
            },
            
            "cemv_support": {
                "type": "Property",
                "value": 1
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_agency_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
        
def test_missing_agency_id_raises_value_error():
    """
    Check that if the 'agency_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'agency_id'
    raw_data = [
        {
            "agency_name": "Agency A1",
            "agency_url": "www.fakeurl.com",
            "agency_timezone": "Europe/Sofia"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_agency_to_ngsi_ld(raw_data)

def test_missing_agency_name_raises_value_error():
    """
    Check that if the 'agency_name' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'agency_name'
    raw_data = [
        {
            "agency_id": "A1",
            "agency_url": "www.fakeurl.com",
            "agency_timezone": "Europe/Sofia"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_agency_to_ngsi_ld(raw_data)

def test_missing_agency_url_raises_value_error():
    """
    Check that if the 'agency_url' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'agency_url'
    raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_timezone": "Europe/Sofia"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_agency_to_ngsi_ld(raw_data)

def test_missing_agency_timezone_raises_value_error():
    """
    Check that if the 'agency_timezone' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'agency_timezone'
    raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_url": "www.fakeurl.com",
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_agency_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide all required fields with an empty optional field
    raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_url": "https://www.fakeurl.com",
            "agency_timezone": "Europe/Sofia",
            "agency_lang": ""
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:A1",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": "Agency A1"
            },
                        
            "agency_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
            
            "agency_timezone": {
                "type": "Property", 
                "value": "Europe/Sofia"
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_agency_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_multiple_entities():
    """
    Check if the raw data contains 2 entities, 
    after the transformation 2 entites are returned from the function call
    """
    # Provide 2 entities
    raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_url": "https://www.fakeurl.com",
            "agency_timezone": "Europe/Sofia",
        },
        {
            "agency_id": "A2",
            "agency_name": "Agency A2",
            "agency_url": "http://www.fakeurl.com",
            "agency_timezone": "Europe/Sofia",
        }
    ]
    
    # Get result from the function call
    result = gtfs_static_agency_to_ngsi_ld(raw_data)
    
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
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_url": "https://www.fakeurl.com",
            "agency_timezone": "Europe/Sofia",
            "unkown_field": "unknown_value"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:A1",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": "Agency A1"
            },
                        
            "agency_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
            
            "agency_timezone": {
                "type": "Property", 
                "value": "Europe/Sofia"
            }
        }
    ]
    
    result = gtfs_static_agency_to_ngsi_ld(raw_data)
    
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the an optional field contains white space as a value, that field will be removed
    """
    # Provide all required fields with an optional field whith a white space as a value
    raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Agency A1",
            "agency_url": "http://www.fakeurl.com",
            "agency_timezone": "Europe/Sofia",
            "agency_lang": " "
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:A1",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": "Agency A1"
            },
                        
            "agency_url": {
                "type": "Property", 
                "value": "http://www.fakeurl.com"
            },
            
            "agency_timezone": {
                "type": "Property", 
                "value": "Europe/Sofia"
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_agency_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
     
def test_empty_agency_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_agency_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_agency_to_ngsi_ld(raw_data) == []