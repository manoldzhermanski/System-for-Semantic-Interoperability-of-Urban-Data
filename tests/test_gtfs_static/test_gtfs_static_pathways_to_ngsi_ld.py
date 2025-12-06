import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_pathways_to_ngsi_ld

def test_valid_gtfs_pathways_conversion():
    """
    Check that if all fields of GTFS Pathway are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S1"
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S2"
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": 1
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": 0
            },
            
            "length": {
                "type": "Property",
                "value": 200.56
            },
            
            "traversal_time": {
                "type": "Property",
                "value": 6.4
            },
            
            "stair_count": {
                "type": "Property",
                "value": -4
            },
            
            "max_slope": {
                "type": "Property",
                "value": -0.3
            },
            
            "min_width": {
                "type": "Property",
                "value": 0.01
            },
            
            "signposted_as": {
                "type": "Property",
                "value": "OK"
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": "OK"
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_pathways_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_missing_pathway_id_raises_value_error():
    """
    Check that if 'pathway_id' is missing, a ValueError is raised
    """
    # Provide all fields without 'pathway_id' 
    raw_data = [
        {
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]
        
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_missing_from_stop_id_raises_value_error():
    """
    Check that if 'from_stop_id' is missing, a ValueError is raised
    """
    # Provide all fields without 'from_stop_id'        
    raw_data = [
        {
            "pathway_id": "P1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]
        
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_missing_to_stop_id_raises_value_error():
    """
    Check that if 'to_stop_id' is missing, a ValueError is raised
    """
    # Provide all fields without 'to_stop_id'
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_missing_pathway_mode_raises_value_error():
    """
    Check that if 'pathway_mode' is missing, a ValueError is raised
    """
    # Provide all fields without 'pathway_mode'
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_pathway_mode_invalid_value_raises_value_error():
    """
    Check that if 'pathway_mode' is not in the range [1,7], a ValueError is raised
    """
    # Provide all fields without 'is_bidirectional'
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "0",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_missing_is_bidirectional_raises_value_error():
    """
    Check that if 'is_bidirectional' is missing, a ValueError is raised
    """
    # Provide all fields without 'is_bidirectional'
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_is_bidirectional_invalid_value_raises_value_error():
    """
    Check if value if 'is_bidirectional' is not in the range [0, 1], a ValueError is raised
    """
    # Provide all fields with 'is_bidirectional' having a value of -1
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "-1",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_negative_length_raises_value_error():
    """
    Check if 'length' has a negative value, ValueError is raised
    """
    # Provide all fields with 'length' having a value negative value
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "-200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_negative_or_zero_traversal_time_raises_value_error():
    """
    Check if 'raversal_time' field has a value <= 0, a ValueError is raised
    """
    # Provide all fields with 'traversal_time' having a value of 0
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "0",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_negative_or_zero_min_width_raises_value_error():
    """
    Check if 'min_width' field has a value <= 0, a ValueError is raised
    """
    # Provide all fields with 'min_width' having a value of 0
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "1",
            "max_slope": "-0.3",
            "min_width": "0.0",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide all required fields with an empty optional field
    raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Provide expected result
    expected = [{
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S1"
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S2"
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": 1
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": 0
            },
                        
            "traversal_time": {
                "type": "Property",
                "value": 6.4
            },
            
            "stair_count": {
                "type": "Property",
                "value": -4
            },
            
            "max_slope": {
                "type": "Property",
                "value": -0.3
            },
            
            "min_width": {
                "type": "Property",
                "value": 0.01
            },
            
            "signposted_as": {
                "type": "Property",
                "value": "OK"
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": "OK"
            }
        }]
    
    # Get result of the function call with the raw data
    result = gtfs_static_pathways_to_ngsi_ld(raw_data)

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
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        },
        {
            "pathway_id": "P2",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK"
        }
    ]

    # Get result from the function call
    result = gtfs_static_pathways_to_ngsi_ld(raw_data)
    
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
            "pathway_id": "P1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": "200.56",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK",
            "uknown_field": "unknown_value"
        }
    ]

    # Provide expected result
    expected = [{
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S1"
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S2"
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": 1
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": 0
            },
            
            "length": {
                "type": "Property",
                "value": 200.56
            },
            
            "traversal_time": {
                "type": "Property",
                "value": 6.4
            },
            
            "stair_count": {
                "type": "Property",
                "value": -4
            },
            
            "max_slope": {
                "type": "Property",
                "value": -0.3
            },
            
            "min_width": {
                "type": "Property",
                "value": 0.01
            },
            
            "signposted_as": {
                "type": "Property",
                "value": "OK"
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": "OK"
            }
        }]
    
    # Get result of the function call with the raw data
    result = gtfs_static_pathways_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the a field contains white space as a value, that field will be removed
    """
    # Provide all required fields with a field whith a white space as a value
    raw_data = [
        {
            "pathway_id": " P1 ",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            "pathway_mode": "1",
            "is_bidirectional": "0",
            "length": " 200.56 ",
            "traversal_time": "6.4",
            "stair_count": "-4",
            "max_slope": "-0.3",
            "min_width": "0.01",
            "signposted_as": "OK",
            "reversed_signposted_as": "OK",
        }
    ]

    # Provide expected result
    expected = [{
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S1"
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsStop:S2"
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": 1
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": 0
            },
            
            "length": {
                "type": "Property",
                "value": 200.56
            },
            
            "traversal_time": {
                "type": "Property",
                "value": 6.4
            },
            
            "stair_count": {
                "type": "Property",
                "value": -4
            },
            
            "max_slope": {
                "type": "Property",
                "value": -0.3
            },
            
            "min_width": {
                "type": "Property",
                "value": 0.01
            },
            
            "signposted_as": {
                "type": "Property",
                "value": "OK"
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": "OK"
            }
        }]
    
    # Get result of the function call with the raw data
    result = gtfs_static_pathways_to_ngsi_ld(raw_data)

    # Check that the result is as expected
    assert result == expected

def test_empty_pathways_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_pathways_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_pathways_to_ngsi_ld(raw_data) == []