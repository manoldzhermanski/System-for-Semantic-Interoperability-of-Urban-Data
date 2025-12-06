import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_routes_to_ngsi_ld

def test_valid_gtfs_routes_conversion():
    """
    Check that if all fields of GTFS Route are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "F-T"
            },
            
            "name": {
                "type": "Property", 
                "value": "FROM-TO"
            },
            
            "description": {
                "type": "Property", 
                "value": "Descr"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 0
            },
            
            "route_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
            
            "routeColor": {
                "type": "Property", 
                "value": "000000"
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": 0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_routes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_missing_route_id_raises_value_error():
    
    # Provide raw data
    raw_data = [
        {
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)
    pass

def test_missing_route_agency_id_raises_value_error():
    
    # Provide raw data
    raw_data = [
        {
            "route_id": "R1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)

def test_missing_route_short_name_raises_value_error():
    
    # Provide raw data
    raw_data = [
        {
            "route_id": "R1",
            "agency_id": "A1",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)

def test_missing_route_long_name_raises_value_error():
    
    # Provide raw data
    raw_data = [
        {
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)

def test_missing_route_type_raises_value_error():
    
    # Provide raw data
    raw_data = [
        {"route_id": "R1",
         "agency_id": "A1",
         "route_short_name": "F-T",
         "route_long_name": "FROM-TO",
         "route_desc": "Descr",
         "route_url": "https://www.fakeurl.com",
         "route_color": "000000",
         "route_text_color": "FFFFFF",
         "route_sort_order": "0",
         "continuous_pickup": "0",
         "continuous_drop_off": "0"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide all required fields with an empty optional field
    raw_data = [
        {
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "F-T"
            },
            
            "name": {
                "type": "Property", 
                "value": "FROM-TO"
            },
            
            "description": {
                "type": "Property", 
                "value": "Descr"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 0
            },
            
            "route_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
                        
            "routeTextColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": 0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_routes_to_ngsi_ld(raw_data)
    
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
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        },
        {
            "route_id": "R2",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
    # Get result from the function call
    result = gtfs_static_routes_to_ngsi_ld(raw_data)
    
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
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": "0",
            "route_desc": "Descr",
            "route_url": "https://www.fakeurl.com",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0",
            "continuous_pickup": "0",
            "continuous_drop_off": "0",
            "unknown_field": "unknown_value"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "F-T"
            },
            
            "name": {
                "type": "Property", 
                "value": "FROM-TO"
            },
            
            "description": {
                "type": "Property", 
                "value": "Descr"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 0
            },
            
            "route_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
            
            "routeColor": {
                "type": "Property", 
                "value": "000000"
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": 0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_routes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the a field contains white space as a value, that field will be removed
    """
    raw_data = [
        {
            "route_id": "R1",
            "agency_id": "A1",
            "route_short_name": "F-T",
            "route_long_name": "FROM-TO",
            "route_type": " 0",
            "route_desc": "Descr",
            "route_url": " https://www.fakeurl.com ",
            "route_color": "000000",
            "route_text_color": "FFFFFF",
            "route_sort_order": "0 ",
            "continuous_pickup": "0",
            "continuous_drop_off": "0"
        }
    ]
    
        # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "F-T"
            },
            
            "name": {
                "type": "Property", 
                "value": "FROM-TO"
            },
            
            "description": {
                "type": "Property", 
                "value": "Descr"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 0
            },
            
            "route_url": {
                "type": "Property", 
                "value": "https://www.fakeurl.com"
            },
            
            "routeColor": {
                "type": "Property", 
                "value": "000000"
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": 0
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_routes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_empty_fare_attributes_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_routes_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_routes_to_ngsi_ld(raw_data) == []