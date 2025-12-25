import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_stops_to_ngsi_ld

def test_gtfs_static_stops_to_ngsi_ld():
    """
    Unit test for gtfs_static_stops_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Stop
    sample_raw_data = [
        {
            "stop_id": "STOP_1",
            "stop_name": "NAME_1",
            "stop_lon": "23.3219",
            "stop_lat": "42.6977",
            "location_type": "0"
            },
        {
            "stop_id": "STOP_2",
            "stop_name": "NAME_2",
            "stop_lon": "23.3219",
            "stop_lat": "42.6977",
            "location_type": "1"
         }
        ]

    # Mock result from parse_gtfs_stops_data
    parsed_data = [
        {
            "stop_id": "S1",
            "stop_name": "N1",
            "stop_lon": 23.3219,
            "stop_lat": 42.6977,
            "location_type": 0
            },
        {
            "stop_id": "S2",
            "stop_name": "N2",
            "stop_lon": 23.3219,
            "stop_lat": 42.6977,
            "location_type": 1
         }
        ]
        
    # Mock result from convert_gtfs_stops_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsStop:S1",
            "type": "GtfsStop",
            "name": {"type": "Property", "object": "N1"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.3219, 42.6977],},},
            "location_type": {"type": "Property", "value": 0},
            },
        {
            "id": "urn:ngsi-ld:GtfsStop:S2",
            "type": "GtfsStop",
            "name": {"type": "Property", "object": "N2"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.3219, 42.6977],},},
            "location_type": {"type": "Property", "value": 1},
            },
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsStop:S1",
            "type": "GtfsStop",
            "name": {"type": "Property", "object": "N1"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.3219, 42.6977],},},
            "location_type": {"type": "Property", "value": 0}
            },
        {
            "id": "urn:ngsi-ld:GtfsStop:S2",
            "type": "GtfsStop",
            "name": {"type": "Property", "object": "N2"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.3219, 42.6977],},},
            "location_type": {"type": "Property", "value": 1}
            }
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
    
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_stops_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_stops_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_stops_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
        
            # Function call result from gtfs_static_stops_to_ngsi_ld
            result = gtfs_static_stops_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_stops_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_stops_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_stops_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2