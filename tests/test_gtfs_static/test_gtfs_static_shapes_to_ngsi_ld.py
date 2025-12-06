import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_shapes_to_ngsi_ld

def test_valid_gtfs_shapes_conversion():
    """
    Check that if all fields of GTFS Shape are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsShape:S1",
            "type": "GtfsShape",
            
            "name": {
                "type": "Property",
                "value": "S1"
                },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [[23.234, 42.033]]
                }
            },
            
            "distanceTravelled": {
                "type": "Property",
                "value": [5]
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_shapes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_missing_shape_id_raises_value_error():
    """
    Check that if the 'shape_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'shape_id'
    raw_data = [
        {
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_shapes_to_ngsi_ld(raw_data)
    
def test_missing_shape_pt_lat_raises_value_error():
    """
    Check that if the 'shape_pt_lat' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'shape_pt_lat'
    raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        }
    ]
   
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_shapes_to_ngsi_ld(raw_data)
    
def test_missing_shape_pt_lon_raises_value_error():
    """
    Check that if the 'shape_pt_lon' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'shape_pt_lon'
    raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_shapes_to_ngsi_ld(raw_data)

def test_missing_shape_pt_sequence_raises_value_error():
    """
    Check that if the 'shape_pt_sequence' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'shape_pt_sequence'
    raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_dist_traveled": "5"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_shapes_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide raw data
    raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": ""
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsShape:S1",
            "type": "GtfsShape",
            
            "name": {
                "type": "Property",
                "value": "S1"
                },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [[23.234, 42.033]]
                }
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_shapes_to_ngsi_ld(raw_data)
    
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
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        },
                {
            "shape_id": "S1",
            "shape_pt_lat": "42.133",
            "shape_pt_lon": "23.134",
            "shape_pt_sequence": "2",
            "shape_dist_traveled": "7"
        },
        {
            "shape_id": "S2",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5"
        },
    ]
    
    # Get result from the function call
    result = gtfs_static_shapes_to_ngsi_ld(raw_data)
    
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
            "shape_id": "S1",
            "shape_pt_lat": "42.033",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "5",
            "unknown_field": "unknown_value"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsShape:S1",
            "type": "GtfsShape",
            
            "name": {
                "type": "Property",
                "value": "S1"
                },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [[23.234, 42.033]]
                }
            },
            
            "distanceTravelled": {
                "type": "Property",
                "value": [5]
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_shapes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the a field contains white space as a value, that field will be removed
    """
    # Provide raw data
    raw_data = [
        {
            "shape_id": " S1",
            "shape_pt_lat": "42.033 ",
            "shape_pt_lon": "23.234",
            "shape_pt_sequence": " 1 ",
            "shape_dist_traveled": "5"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsShape:S1",
            "type": "GtfsShape",
            
            "name": {
                "type": "Property",
                "value": "S1"
                },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [[23.234, 42.033]]
                }
            },
            
            "distanceTravelled": {
                "type": "Property",
                "value": [5]
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_shapes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_empty_shapes_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_shapes_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_shapes_to_ngsi_ld(raw_data) == []