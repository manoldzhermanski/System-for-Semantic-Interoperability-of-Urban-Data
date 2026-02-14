import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_routes_to_ngsi_ld
        
def test_gtfs_routes_to_ngsi_ld():
    """
    Unit test for gtfs_static_routes_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Route
    sample_raw_data = [
        {
            "route_id": "R1",
            "route_short_name": "Bus Route 5",
            "route_type": "3",
            },
        {
            "route_id": "R2",
            "route_short_name": "Bus Route 6",
            "route_type": "3",
            },
        ]

    # Mock result from parse_gtfs_routes_data
    parsed_data = [
        {
            "route_id": "R1",
            "route_short_name": "Bus Route 5",
            "route_type": 3,
            },
        {
            "route_id": "R2",
            "route_short_name": "Bus Route 6",
            "route_type": 3,
            },
        ]
    
    city = "Sofia"
    
    # Mock result from convert_gtfs_routes_to_ngsi_ld
    converted_data = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 5",},
            "routeType": {"type": "Property", "value": 3}
            },
        {
            "id": f"urn:ngsi-ld:GtfsRoute:{city}:R2",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 6",},
            "routeType": {"type": "Property", "value": 3}
            },
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 5",},
            "routeType": {"type": "Property", "value": 3}
            },
        {
            "id": f"urn:ngsi-ld:GtfsRoute:{city}:R2",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 6",},
            "routeType": {"type": "Property", "value": 3}
            },
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
        
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_routes_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_routes_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_routes_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
            
            # Function call result from gtfs_static_routes_to_ngsi_ld
            result = gtfs_static_routes_to_ngsi_ld(sample_raw_data, city)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_routes_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_routes_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0], city)
    mock_validate.assert_any_call(parsed_data[1], city)

    # Check that convert_gtfs_routes_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2