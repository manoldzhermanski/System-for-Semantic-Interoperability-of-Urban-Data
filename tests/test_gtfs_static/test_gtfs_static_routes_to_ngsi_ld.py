import pytest
from unittest.mock import patch
from gtfs_static.gtfs_static_utils import gtfs_static_routes_to_ngsi_ld

# Mock function behavior
@patch("gtfs_static.gtfs_static_utils.remove_none_values")
@patch("gtfs_static.gtfs_static_utils.convert_gtfs_routes_to_ngsi_ld")
@patch("gtfs_static.gtfs_static_utils.validate_gtfs_routes_entity")
@patch("gtfs_static.gtfs_static_utils.parse_gtfs_routes_data")
def test_gtfs_routes_to_ngsi_ld(mock_parse, mock_validate, mock_convert, mock_remove_none):
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
    
    mock_parse.side_effect = parsed_data
    
    # Mock result from convert_gtfs_routes_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 5",},
            "routeType": {"type": "Property", "value": 3}
            },
        {
            "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R2",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 6",},
            "routeType": {"type": "Property", "value": 3}
            },
        ]
    
    mock_convert.side_effect = converted_data
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R1",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 5",},
            "routeType": {"type": "Property", "value": 3}
            },
        {
            "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R2",
            "type": "GtfsRoute",
            "shortName": {"type": "Property", "value": "Bus Route 6",},
            "routeType": {"type": "Property", "value": 3}
            },
        ]
    
    mock_remove_none.side_effect = cleaned_data
    
    # Function call result from gtfs_static_routes_to_ngsi_ld
    result = gtfs_static_routes_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_routes_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_routes_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_routes_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2